from pathlib import Path
import zipfile
root=Path(__file__).resolve().parents[1]
output=root/'dist/dispatch.zip'; output.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
    for path in sorted(root.rglob('*')):
        if path.is_file() and not any(p in {'dist','.state','__pycache__','.git'} for p in path.relative_to(root).parts):
            z.write(path,path.relative_to(root))
print(output)
