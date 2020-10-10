# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['G:\\Desktop\\tw_dev\\pop'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries+[('oraociei11.dll','C:\\Documents and Settings\\tw\\Desktop\\instantclient\\oraociei11.dll','BINARY')],
          a.zipfiles,
          a.datas,
          name='main',
          debug=False,
          strip=False,
          upx=True,
          console=False )
