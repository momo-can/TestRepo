def main(**kwargs):
    configData = config.getConfig(**kwargs)
    recipes = configData.get('recipes', [])

    pluginDir = config.getPluginDir()

    print('*' * 30)
    print('Custom Playblast')
    print('*' * 30)

    userInput = kwargs
    for i, recipeInfo in enumerate(recipes):
        pluginName = recipeInfo.get('pluginName', '')
        flags = recipeInfo.get('flags', {})
        typeIs = recipeInfo.get('typeIs', '')

        pluginPath = '/'.join([
            pluginDir,
            pluginName
        ])

        if typeIs == 'command':
            cmd = 'python("{}")'.format(pluginName)
            mel.eval(cmd)
        elif typeIs == 'file':
            if not os.path.isfile(pluginPath):
                print('> Not found.')
                print(pluginPath)
                break

            mod = imp.load_source(
                'buildModule{}'.format(i),
                pluginPath
            )

            userInput['flags'] = flags
            userInput.update(mod.main(**userInput))
            print('> {}'.format(pluginPath))

    print('')
    return {}
