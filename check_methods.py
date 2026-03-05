from plugins.converters.to_epub import ToEpubPlugin
methods = [m for m in dir(ToEpubPlugin) if not m.startswith('__')]
print('插件方法：')
for m in methods[:30]:
    print(f'  - {m}')
