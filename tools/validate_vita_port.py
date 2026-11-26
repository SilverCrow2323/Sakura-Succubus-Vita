#!/usr/bin/env python3
"""Validate PS Vita package metadata and LiveArea assets using Python's stdlib."""
from __future__ import annotations
import re, struct, sys
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TITLE_ID_RE=re.compile(r"ux0:/?app/([A-Z0-9]{9})(?:/|\\b)")
def read_sfo(path:Path)->dict[str,str]:
    data=path.read_bytes()
    if len(data)<20: raise ValueError("param.sfo is shorter than its header")
    magic,_version,key_off,data_off,count=struct.unpack_from("<4sIIII",data,0)
    if magic!=b"\x00PSF": raise ValueError("invalid PSF signature")
    if count>4096 or 20+count*16>len(data): raise ValueError("entry table is out of bounds")
    result={}
    for i in range(count):
        pos=20+i*16
        key_rel,_fmt,length,max_len,value_rel=struct.unpack_from("<HHIII",data,pos)
        ks,vs=key_off+key_rel,data_off+value_rel
        if ks>=len(data) or vs>len(data): raise ValueError(f"entry {i} points outside param.sfo")
        ke=data.find(b"\0",ks)
        if ke<0 or length>max_len or vs+length>len(data): raise ValueError(f"entry {i} has invalid bounds")
        key=data[ks:ke].decode("utf-8")
        value=data[vs:vs+length].split(b"\0",1)[0].decode("utf-8",errors="replace")
        result[key]=value
    return result
def validate()->list[str]:
    errors=[]
    sfo_files=sorted(p for p in ROOT.rglob("param.sfo") if p.parent.name=="sce_sys")
    if len(sfo_files)!=1: return [f"Expected one sce_sys/param.sfo, found {len(sfo_files)}"]
    sfo_path=sfo_files[0]; app_root=sfo_path.parent.parent
    livearea=app_root/"sce_sys"/"livearea"/"contents"
    template=livearea/"template.xml"
    for p in (sfo_path,template,livearea/"bg.png",livearea/"startup.png"):
        if not p.is_file(): errors.append(f"Missing required file: {p.relative_to(ROOT)}")
    title_id=""
    try:
        values=read_sfo(sfo_path); title_id=values.get("TITLE_ID","")
        if not re.fullmatch(r"[A-Z0-9]{9}",title_id): errors.append(f"Invalid TITLE_ID: {title_id!r}")
        if not values.get("TITLE","").strip(): errors.append("TITLE is missing in param.sfo")
    except (OSError,ValueError,UnicodeError,struct.error) as exc: errors.append(f"Cannot read param.sfo: {exc}")
    if template.is_file():
        try:
            root=ET.parse(template).getroot()
            if root.tag!="livearea": errors.append("LiveArea root must be <livearea>")
            refs=[n.text.strip() for n in root.iter() if n.tag in {"image","startup-image"} and n.text and n.text.strip()]
            if not refs: errors.append("LiveArea template contains no image references")
            for ref in refs:
                target=(livearea/ref).resolve()
                if not target.is_relative_to(livearea.resolve()): errors.append(f"Asset escapes LiveArea directory: {ref}")
                elif not target.is_file(): errors.append(f"Referenced LiveArea asset is missing: {ref}")
        except (ET.ParseError,OSError,ValueError) as exc: errors.append(f"Invalid LiveArea XML: {exc}")
    if title_id:
        docs=[p for p in (ROOT/"README.md",ROOT/"readme.md") if p.is_file()]
        docs += [p for p in (ROOT/"wiki-source").glob("Installation*.md") if p.is_file()]
        ids=set()
        for doc in docs: ids.update(TITLE_ID_RE.findall(doc.read_text(encoding="utf-8")))
        if not ids: errors.append("No ux0:/app/TITLE_ID installation path found in README/wiki installation notes")
        for value in sorted(ids):
            if value!=title_id: errors.append(f"Documentation uses {value}; param.sfo declares {title_id}")
    return errors
if __name__=="__main__":
    errors=validate()
    if errors:
        for error in errors: print("ERROR:",error,file=sys.stderr)
        raise SystemExit(1)
    print("Vita package metadata, LiveArea assets and documented title ID: OK")
