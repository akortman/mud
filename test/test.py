import unittest
import music21

if __name__ == '__main__':
    # mute music21 warnings.
    music21.environment.UserSettings()['warnings'] = 0

    loader = unittest.TestLoader()
    start_dir = './test/'
    suite = loader.discover(start_dir)

    runner = unittest.TextTestRunner()
    runner.run(suite)