from detector import *


action = MainAction()
detector = MainDetector()


def main():
    print('[INFO] Getting invasion..')
    action.get_invasion()
    while True:
        detector.battle()
        detector.detect_poke()
        detector.close_pokestop()
        detector.open_pokestop()
        detector.timers_check()
        detector.check_exit()
        detector.check_speed()


if __name__ == '__main__':
    main()
