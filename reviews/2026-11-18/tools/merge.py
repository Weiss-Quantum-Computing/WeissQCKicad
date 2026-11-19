import json,glob,os,sys,re
S=sys.argv[1]
GROUPS=["Supertime timing boards","Digital buffer evaluation boards","Strobe, DDS timing and small logic","Lattice intensity lock","Magnetic noise suppression","Bias coil drivers","Summing circuits","Filters and phase shifters","VCA and difference amplifier"]
FILEGROUP={"supertime_mux":0,"supertime_trigger":0,"digital_buffer":1,"strobe_logic":2,"intensity_lock":3,"magnetic_noise":4,"bias_coil":5,"summing":6,"filters":7,"vca_isolation":8}
RANK={"built board":0,"board laid out":1,"schematic only":2,"unfinished":3,"superseded":4,"empty":5}
FIG={ # id: (figure key in figs/out, figure base name)
"supertime-multiplexer":("Supertime Multiplexer__Supertime Multiplexer","Supertime Multiplexer"),
"supertime-external-trigger":("Supertime External Trigger__Supertime External Trigger","Supertime External Trigger"),
"digital-buffer-eval-v1":("Digital Buffer IC evaluation board V1__Digital Buffer IC evaluation board","Digital Buffer eval board V1"),
"digital-buffer-eval-v2":("Digital Buffer IC evaluation board V2__Digital Buffer IC evaluation board V2","Digital Buffer eval board V2"),
"strobe-dds-timing":("Strobe generator and DDS Timing Control__Strobe generator and DDS Timing Control","Strobe generator and DDS timing control"),
"jr65rc-unknown":("JR65RC_Unknown__JR65RC_Unknown","JR65RC unknown board"),
"and-gate-rf-trigger":("JR65RC_Unknown__AND_Gate__AND_Gate","AND gate for RF trigger"),
"opamp-eval-board":("Opamp Eval Board__Opamp Eval Board","Opamp eval board"),
"lattice-intensity-lock-v4":("Intensity_Lock__Lattice_Intensity_Lock","Lattice intensity lock (newest, Intensity_Lock folder)"),
"lattice-intensity-lock-ver2":("Lattice_Intensity_Lock_ver2__Lattice_Intensity_Lock","Lattice intensity lock ver2"),
"lattice-intensity-lock-v1":("Lattice_Intensity_Lock__Lattice_Intensity_Lock","Lattice intensity lock first board"),
"lattice-intensity-lock-copy":("Lattice_Intensity_Lock Copy__Lattice_Intensity_Lock","Lattice intensity lock early draft"),
"magnetic-noise-cancellation-v1":("Magnetic_Noise_Suppression_Circuit__Magnetic_Noise_Cancellation","Magnetic noise cancellation"),
"bias-coil-driver-high-current":("Bias Coil Driver High Current__Bias Coil Driver High Current","Bias coil driver high current"),
"bias-coil-driver-full":("Bias Coil Driver Full__Bias Coil Driver Full","Bias coil driver full"),
"bias-coil-driver-full002":("Bias Coil Driver Full002__Bias Coil Driver Full002","Bias coil driver full002 (2022)"),
"bias-coil-driver-early":("Bias Coil Driver__Bias Coil Driver","Bias coil driver early stub"),
"summing-circuit-v5":("Summing Circuit V5__Summing Circuit V5","Summing circuit V5"),
"bias-coil-driver-v2-apr2022":("Bias Coil Driver V2__Bias Coil Driver","Bias coil driver summing (April 2022)"),
"bias-coil-driver-v3-may2022":("Bias Coil Driver V2__Bias Coil DriverV3","Bias coil driver V3 (May 2022)"),
"summing-circuit-v4-may2022":("Bias Coil Driver V2__Summing Circuit V4","Summing circuit V4"),
"ao847-simple-summing-2019":("BMP","Simple summing circuit for AO847 (2019)"),
"active-twin-t":("Active Twin T__Active Twin T","Active twin-T notch"),
"second-order-phase-shifter":("Second Order Phase Shifter__Second Order Phase Shifter","Second order phase shifter"),
"5-stage-butterworth-bandpass":("5 Stage butterworth Bandpass Filter__5 Stage butterworth Bandpass Filter","5 stage Butterworth bandpass"),
"60hz-harmonic-generation-filtering":("60 Hz Harmonic generation and filtering__60 Hz Harmonic generation and filtering","60 Hz harmonic generation and filtering"),
"vca810-vca":("VCA__VCA","VCA810 voltage-controlled amplifier"),
"amp03-iso-amp":("Isolation Amplifier__Isolation Amplifier","Isolation amplifier (AMP03 difference amp)"),
}
FOLDER={"bias-coil-driver-full002":"../Bias Coil Driver Full002.kicad_sch (loose file in Electronics, outside KiCAD)","lattice-intensity-lock-v4":"../Intensity_Lock (in Electronics, outside KiCAD)"}
# overrides: (circuit id, title prefix) -> dict of replacements
OV={
("magnetic-noise-cancellation-v1","5 V LDO U9"):dict(severity="minor",title="U9 is drawn with a 5.5 V regulator symbol but takes +15 V in",
  detail="U9 is fed from +15 V. The part named in the schematic, LDK320M50R, is rated for 18 V operating and 20 V absolute maximum, so it is within its limits. The library symbol used is a TPS7A05, which is a 5.5 V part; fitting that or a similar low-voltage LDO would destroy it. The LDO also drops 10 V, so it runs warm above a few tens of mA.",
  evidence="+15V net includes U9.1 (IN) and U9.3 (EN); value LDK320M50R; symbol TPS7A0531PDBV. LDK320 ratings from the ST datasheet DS11321 (looked up).",
  fix="Keep the LDK320M50R and correct the symbol. Check that U9 is not hot on the built board.",confidence="high",checked=True),
("magnetic-noise-cancellation-v1","R17 and R18"):dict(severity="minor",title="R17 and R18 are either/or links but both are drawn as fitted",
  detail="R17 bypasses the VCA810 gain stage and R18 takes its output; the schematic note says the gain stage may not be necessary. Both are 0 Ω with no do-not-fit mark. With both fitted, the VCA810 output is shorted to its own input and to U16's output.",
  fix="Fit only one. Check which is fitted on the built board and mark the other as not fitted in the schematic.",checked=True),
("amp03-iso-amp","Not an isolation amplifier"):dict(severity="major",title="Not galvanically isolated: it is a difference amplifier",
  detail="The board is labelled ISOLATION AMP, but U1 is an AMP03 unity-gain difference amplifier with one ground and one pair of supplies. It breaks ground loops by rejecting common-mode voltage within its input range. It gives no safety isolation and no protection beyond that range.",
  fix="Rename it (differential receiver or ground-loop breaker). Do not use it where true isolation is needed.",checked=True),
("bias-coil-driver-high-current","Status inverter"):dict(title="Status inverter has no defined supply in the schematic",
  detail="The 74LVC1GU04 that drives the status LED has its ground pin on V−. Its VCC node has only capacitors on it: the wire toward the GND symbol stops short, and the 5 V regulator that the Full version has here is missing. If VCC were wired straight to GND, the part would see the whole negative rail (15 V at ±15 V), above its 6.5 V limit. The board does not include this inverter at all.",
  evidence="U?.3 (GND) on -VDC; U?.5 (VCC) is on no net with a source; in the schematic image the VCC wire ends before the GND / 0.33 µF node. DRC: footprint for U? missing from the board.",
  fix="Add a regulator that makes V− + 5 V for the inverter (as in the Full schematic, with its pins corrected) before adding this to the board.",confidence="medium",checked=True),
("lattice-intensity-lock-v4","R11 and R12"):dict(title="R11 and R12 are either/or links but both are listed as fitted",
  detail="R11 sends the unclamped signal straight to the output connector; R12 sends the clamped one. They are meant as a choice, but both are 0 Ω in the schematic and BOM with no do-not-fit mark. With both fitted the zener clamp is defeated and the AOM driver sees the unclamped voltage.",
  fix="Check which is fitted on the working board. Fit only R12 (clamp in use) unless there is a reason to bypass it, and mark R11 as not fitted."),
}
CHECKED=[("summing-circuit-v5","R3 and R10"),("digital-buffer-eval-v2","Part is HC"),("5-stage-butterworth-bandpass","Each section"),("5-stage-butterworth-bandpass","Stage-4"),("5-stage-butterworth-bandpass","Filter output"),("supertime-external-trigger","Gate inputs float"),("lattice-intensity-lock-v4","J4 pin numbers"),("amp03-iso-amp","Power connector pin order"),("vca810-vca","Power connector pin order")]
out=[]
for f in sorted(glob.glob(S+'/out/*.json')):
    key=os.path.basename(f)[:-5]
    if key in('circuits_merged',): continue
    d=json.load(open(f))
    for c in d['circuits']:
        cid=c['id']
        c['group']=GROUPS[FILEGROUP[key]]; c['_g']=FILEGROUP[key]
        if cid in FOLDER: c['folder']=FOLDER[cid]
        if cid=='ao847-simple-summing-2019': c['status_note']=c.get('status_note','')
        for n,i in enumerate(c['issues']):
            i['checked']= (cid=='supertime-multiplexer')
            for (oc,pre),rep in OV.items():
                if oc==cid and i['title'].startswith(pre): i.update(rep)
            for (oc,pre) in CHECKED:
                if oc==cid and i['title'].startswith(pre): i['checked']=True
            if i['severity']=='critical' and c['status'] in('unfinished','schematic only','superseded','empty'): i['severity']='major'
        SEV=['critical','major','minor','note']
        c['issues'].sort(key=lambda i:SEV.index(i['severity']))
        for n,i in enumerate(c['issues']): i['id']='i%02d'%(n+1)
        for n,p in enumerate(c['unknown_parts']):
            p['id']='p%02d'%(n+1)
            if cid=='magnetic-noise-cancellation-v1' and p['refs']=='U9': p['suggested']='LDK320M50R (18 V input rating); fix the symbol'
        c['figkey'],c['figname']=FIG[cid]
        out.append(c)
out.sort(key=lambda c:(c['_g'],RANK.get(c['status'],9),-(int((c.get('last_modified') or '0')[:4] or 0))))
for n,c in enumerate(out): c['order']=n+1
json.dump(out,open(S+'/circuits_merged.json','w'),ensure_ascii=False,indent=1)
import collections
print(len(out),'circuits'); tot=collections.Counter(i['severity'] for c in out for i in c['issues']); print(tot, 'checked',sum(i['checked'] for c in out for i in c['issues']), 'parts',sum(len(c['unknown_parts']) for c in out))
for c in out: print(c['order'],c['group'][:18],'|',c['id'],'|',c['status'],'|',c['last_modified'],'|',len(json.dumps(c)))
unmatched=[k for k in OV if not any(c['id']==k[0] and any(i['title']==OV[k].get('title') for i in c['issues']) for c in out)]
print('unmatched overrides',unmatched)
