from pathlib import Path
import zipfile,hashlib,shutil,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
WIN=Path('/mnt/c/Users/apexw/Downloads/AI Consciousness - Is Anyone Home/output')
WIN.mkdir(parents=True,exist_ok=True)
files=['Is Anyone Home.pptx','Is Anyone Home.pdf','Is Anyone Home.html','Presenter Guide.pdf','START HERE.txt']
bundle=OUT/'Is Anyone Home - Complete.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name in files:z.write(OUT/name,name)
    for directory in ('source','assets'):
        for p in sorted((ROOT/directory).rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:z.write(p,p.relative_to(ROOT))
with zipfile.ZipFile(bundle) as z:
    assert z.testzip() is None
    assert all('.env' not in Path(n).parts and '.build' not in Path(n).parts for n in z.namelist())
    names=z.namelist()
shutil.copy2(ROOT/'.build/slides-pdf/01.png',WIN/'Preview.png')
hashes={}
for name in files+[bundle.name]:
    dst=WIN/name
    if dst.exists():
        if hashlib.sha256(dst.read_bytes()).digest()!=hashlib.sha256((OUT/name).read_bytes()).digest():
            shutil.copy2(OUT/name,dst)
    else:shutil.copy2(OUT/name,dst)
    a=hashlib.sha256((OUT/name).read_bytes()).hexdigest();b=hashlib.sha256(dst.read_bytes()).hexdigest();assert a==b
    hashes[name]={'bytes':dst.stat().st_size,'sha256':a}
(ROOT/'.build/delivery-verification.json').write_text(json.dumps({'files':hashes,'bundle_entries':names},indent=2))
print(json.dumps({'destination':str(WIN),'files':hashes,'bundle_entries':len(names)},indent=2))
