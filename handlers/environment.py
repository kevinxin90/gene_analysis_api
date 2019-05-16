import os
import sys
from os import path

lib_path = os.path.abspath(os.path.join('..', 'moduels'))
sys.path.append(path.dirname(path.dirname(path.abspath(lib_path))))

from modules.Mod1A_functional_sim import FunctionalSimilarity
from modules.Mod1E_interactions import GeneInteractions

