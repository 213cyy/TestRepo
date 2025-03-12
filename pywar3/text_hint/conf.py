

root, folder, file = __file__.rsplit('\\', 2)
ROOT = root + "/"
SUB_ROOT = ROOT + folder + "/"
TEXT_HINT_SHADER_FOLDER = SUB_ROOT + "Shaders/"

UITILE_TEXTURE_FOLDER = folder = SUB_ROOT + "UI/"
UITILE_FILE_LIST = [folder + "HumanUITile01.blp",
                    folder + "HumanUITile02.blp",
                    folder + "HumanUITile03.blp",
                    folder + "HumanUITile04.blp"]
