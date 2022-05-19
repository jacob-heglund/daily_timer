import os
import argparse
import time
import datetime
from playsound import playsound
import plyer.platforms.win.notification
from plyer import notification
import webbrowser
import pdb

parser = argparse.ArgumentParser(description=None)
parser.add_argument('-n', '--n_sessions', default=2, type=int, help="Number of consecutive work sessions you want to plan. Only works for n \in {1, 2} since you're probably not able to do more than two consecutive work sessions.")
parser.add_argument('-w', '--work_length', default=90, type=int, help="Number of minutes per work session")
parser.add_argument('-r', '--rest_length', default=20, type=int, help="Number of minutes per rest session")
parser.add_argument('-d', '--debug_mode', default=False, type=str, choices=('True', 'False'), help="Debug mode")
# parser.add_argument('-d', '--debug_mode', default=True, type=str, choices=('True', 'False'), help="Debug mode")
args = parser.parse_args()

nsdr_url = 'https://youtu.be/pL02HRFk2vo?t=48/'
playlist_url = 'https://www.youtube.com/playlist?list=PLylfBmdQ1h3ZjMnIAA7_wTv9Rh8hR1r9W'


def open_nsdr_url():
    webbrowser.open_new(nsdr_url)


def open_playlist_url():
    webbrowser.open_new(playlist_url)


class Period:
    def __init__(self, period_type, start_time, duration, time_index=0):
        self.period_type = period_type
        self.start_time = start_time
        self.duration = duration
        self.end_time = self.start_time + datetime.timedelta(minutes=duration)
        self.time_index = time_index


class WorkTimer:
    def __init__(self, args):
        self.n_sessions = args.n_sessions
        self.work_length = args.work_length
        self.rest_length = args.rest_length
        self.debug_mode = args.debug_mode
        self.lunch = True
        self.time_format = "%I:%M:%p"
        self.start_work_soundfile = "./resources/message-ringtone-magic.mp3"
        self.start_rest_soundfile = "./resources/fingerlicking-message-tone.mp3"
        self.notification_length = 1

        self.app_name = "Work Timer"
        self.app_icon_path = "./resources/clock.ico"

        if self.debug_mode:
            self.start_time = datetime.datetime(2022, 5, 17, 8, 51)
        else:
            self.start_time = datetime.datetime.now()

        # Cut off any work sessions after the first one so I can have lunch between 11:00 - 11:59 AM
        latest_lunch_start = self.start_time.replace(hour=11, minute=59)
        if self.start_time > latest_lunch_start:
            self.lunch = False

        self.sessions = {}
        self.times = [self.start_time]

        self._create_plan()

        end_times = []
        for session in self.sessions.values():
            for period in session.values():
                end_times.append(period.end_time)
        self.max_end_time = max(end_times)
        self.plan_str = self._print_plan()

        self._run_plan()

    def _create_plan(self):
        for i in range(self.n_sessions):
            self.sessions[i] = {}
            if i == 0:
                if i == self.n_sessions - 1:
                    self._add_work_session(self.sessions[i], final_session=True)
                else:
                    self._add_work_session(self.sessions[i])
            else:
                if self.lunch:
                    self._add_lunch_session(self.sessions[i], self.sessions[i-1])
                else:
                    self._add_work_session(self.sessions[i], self.sessions[i-1])


    def _print_plan(self):
        # show the entire plan for the work sessions, prints to the command line
        plan_str = ""

        for key in self.sessions:
            session = self.sessions[key]
            print_str = ""
            for i in session:
                print_str += session[i].period_type.capitalize() + f" {session[i].start_time.strftime(self.time_format)} - {session[i].end_time.strftime(self.time_format)}"
                print_str += "\n"
            plan_str += print_str

        print(plan_str)
        return plan_str

    def _run_plan(self):
        if self.debug_mode:
            curr_time = datetime.datetime(2022, 5, 17, 10, 00)

        done = False
        prev_period = None
        last_print_len = None

        while not done:
            # every minute get the current time and check which session we're in
            if self.debug_mode:
                curr_time += datetime.timedelta(minutes=1)
            else:
                curr_time = datetime.datetime.now()

            # run a timer for each session in the commandline
            for session in self.sessions.values():
                for period in session.values():
                    if period.start_time <= curr_time < period.end_time:
                        curr_period = period
                        remaining_time_minutes = int(abs((curr_time - period.end_time).total_seconds() / 60))

                        ## printing option 1: updates only the timer
                        # if last_print_len is not None:
                        #     print(" "*last_print_len, end="\r")
                        # msg = f"{period.period_type.capitalize()} --- Remaining time (minutes): {remaining_time_minutes}"
                        # print(msg, end="\r")
                        # last_print_len = len(msg)

                        ## printing option 2: updates the timer and has a little pointer to the current period
                        os.system("cls")
                        tmp_str = self.plan_str.split("\n")
                        tmp_str[curr_period.time_index] += " <--- You are here"
                        for i in range(len(tmp_str)-1):
                            tmp_str[i] += "\n"
                        new_plan_str = ''.join(tmp_str)
                        print(new_plan_str)

                        msg = f"{period.period_type.capitalize()} --- Remaining time (minutes): {remaining_time_minutes}"
                        print(msg)

            # push notification on start of focused work
            if prev_period is None:
                prev_period = curr_period
                playsound(self.start_work_soundfile, block=False)
                title = f"Focused work until {curr_period.end_time.strftime(self.time_format)}"
                msg = f"{self.work_length} minutes of focused work."
                notification.notify(title, msg, app_name=self.app_name, app_icon=self.app_icon_path)

            if curr_period != prev_period:
                if curr_period.period_type == "work":
                    playsound(self.start_work_soundfile, block=False)
                    title = f"Focused work until {curr_period.end_time.strftime(self.time_format)}"
                    msg = f"{self.work_length} minutes of focused work."
                    notification.notify(title, msg, app_name=self.app_name, app_icon=self.app_icon_path)

                elif curr_period.period_type == "rest":
                    playsound(self.start_rest_soundfile, block=False)
                    title = f"Rest until {curr_period.end_time.strftime(self.time_format)}"
                    msg = f"{self.rest_length} minute break, try going on a walk or do some NSDR."
                    notification.notify(title, msg, app_name=self.app_name, app_icon=self.app_icon_path)

            prev_period = curr_period
            if curr_time > self.max_end_time:
                if not self.debug_mode:
                    playsound(self.start_rest_soundfile, block=False)
                    notifier.show_toast("Work session ended", msg=f"Go have some lunch or go on a walk or something.", duration=self.notification_length)
                done = True
                break

            if self.debug_mode:
                time.sleep(0.1)
            else:
                time.sleep(60)

    def _add_work_session(self, session, prev_session=None, final_session=False):
        # work session ends self.work_length minutes after start of work session first
        if prev_session is None:
            session["work"] = Period("work", self.start_time, self.work_length)
        else:
            session["work"] = Period("work", prev_session["rest"].end_time, self.work_length, time_index=prev_session["rest"].time_index + 1)

        if not final_session:
            session["rest"] = Period("rest", session["work"].end_time, self.rest_length, time_index=session["work"].time_index + 1)

    def _add_lunch_session(self, session, prev_session):
        # cut down the work time for this work session to make it end at 11:59 AM for lunch
        work_length = self.work_length
        work_end = prev_session["rest"].end_time + datetime.timedelta(minutes=self.work_length)
        latest_lunch_start = self.start_time.replace(hour=11, minute=59)
        if work_end > latest_lunch_start:
            work_diff_minutes = (latest_lunch_start - work_end).total_seconds() / 60
            work_length = self.work_length - abs(work_diff_minutes)

        session["work"] = Period("work", prev_session["rest"].end_time, work_length, time_index=prev_session["rest"].time_index + 1)


if __name__ == "__main__":
    WorkTimer(args)

