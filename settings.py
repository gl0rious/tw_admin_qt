import yaml


def no_duplicates_constructor(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        value = loader.construct_object(value_node, deep=deep)
        if key in mapping:
            Settings.duplicate_roles.append(key)
            continue
        mapping[key] = value
    return loader.construct_mapping(node, deep)


yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                     no_duplicates_constructor, yaml.SafeLoader)


class Settings:
    @classmethod
    def load(cls, window):
        try:
            cls.duplicate_roles = []
            cls.app_roles = yaml.safe_load(open('form_roles.yaml', encoding='utf-8'))
            cls.settings = yaml.safe_load(open('settings.yaml', encoding='utf-8'))
            roles = set()
            for tab in cls.app_roles.values():
                for group in tab.values():
                    for role_name in group.keys():
                        if role_name in roles:
                            cls.duplicate_roles.append(role_name)
                        roles.add(role_name.upper())
            cls.form_roles = list(roles)
            if cls.duplicate_roles:
                msg = 'duplicate roles : \n'+','.join(Settings.duplicate_roles)
                window.onError('Duplicate roles', msg)
        except FileNotFoundError as exc:
            window.onError('File not found', exc.filename)
