import argparse
import time
import datetime
from plyer import notification
import pdb

parser = argparse.ArgumentParser(description=None)
parser.add_argument('-n', '--n_sessions', default=2, type=int, help="Number of consecutive work sessions you want to plan")
parser.add_argument('-w', '--work_length', default=90, type=int, help="Number of minutes per work session")
parser.add_argument('-r', '--rest_length', default=20, type=int, help="Number of minutes per rest session")
args = parser.parse_args()


class Period:
    def __init__(self, period_type, start_time, duration):
        self.period_type = period_type
        self.start_time = start_time
        self.duration = duration
        self.end_time = self.start_time + datetime.timedelta(minutes=duration)


class WorkTimer:
    def __init__(self, args):
        self.n_sessions = args.n_sessions
        self.work_length = args.work_length
        self.rest_length = args.rest_length
        self.lunch = True

        #TODO bring back in real time after development is done
        # self.start_time = datetime.datetime(2022, 5, 17, 8, 30)
        self.start_time = datetime.datetime.now()

        # Cut off any work sessions after the first one so I can have lunch between 11:00 - 11:59 AM
        latest_lunch_start = self.start_time.replace(hour=11, minute=59)
        if self.start_time > latest_lunch_start:
            self.lunch = False

        self.sessions = {}
        self.times = [self.start_time]

        self._create_plan()
        # self.max_end_time =
        self._print_plan()
        #TODO running the plan and having a timer + notifications is a more significant pain in the ass, but worth it so I don't have to be checking the time constantly
        # self._run_plan()

    def _create_plan(self):
        for i in range(self.n_sessions):
            self.sessions[i] = {}
            if i < 1:
                self._add_work_session(self.sessions[i])
            else:
                if self.lunch:
                    self._add_lunch_session(self.sessions[i], self.sessions[i-1])
                else:
                    self._add_work_session(self.sessions[i], self.sessions[i-1])

    def _print_plan(self):
        # show the entire plan for the work sessions, prints to the command line
        time_format = "%I:%M:%p"

        for key in self.sessions:
            session = self.sessions[key]
            print_str = ""
            for i in session:
                print_str += session[i].period_type.capitalize() + f" {session[i].start_time.strftime(time_format)} - {session[i].end_time.strftime(time_format)}"
                if session[i].period_type == "work":
                    print_str += "\n"
            print(print_str)

    def _run_plan(self):
        #TODO remove after development is done
        curr_time = datetime.datetime(2022, 5, 17, 9, 35)
        done = False
        prev_period = None

        while not done:
            #TODO add after development is done
            # every minute get the current time and check which session we're in
            # curr_time = datetime.datetime.now()

            #TODO remove after development is done
            curr_time += datetime.timedelta(minutes=1)

            # run a timer for each session in the commandline
            for session in self.sessions.values():
                for period in session.values():
                    if period.start_time <= curr_time < period.end_time:
                        curr_period = period
                        remaining_time = (curr_time - period.end_time).total_seconds() / 60
                        print(f"{period.period_type.capitalize()} --- Remaining time: {abs(round(remaining_time, 0))}", end="\r")

                    elif curr_time > self.max_end_time:
                        done = True

            #TODO have some behavior that tells you when your work session is over and to start resting
            ## then you could have the program run in detached mode and don't need to keep a command line open to see it
            ## maybe a notification of some type?
            if prev_period is None:
                prev_period = curr_period

            if curr_period != prev_period:
                if curr_period.period_type == "work":
                    print("rest ended")
                elif curr_period.period_type == "rest":
                    print("work ended")

            prev_period = curr_period

            # have a sound play when the session ends

            ## do behaviors based on the current session

            # TODO add white noise sound as an option during work sesions

            #TODO add after development is done
            time.sleep(0.1)
            # time.sleep(60)

    def _add_work_session(self, session, prev_session=None):
        # work session ends 90 minutes after start of work session first
        if prev_session is None:
            session["work"] = Period("work", self.start_time, self.work_length)
        else:
            session["work"] = Period("work", prev_session["rest"].end_time, self.work_length)

        session["rest"] = Period("rest", session["work"].end_time, self.rest_length)

    def _add_lunch_session(self, session, prev_session):
        # cut down the work time for this work session to make it end at 11:59 AM for lunch
        work_length = self.work_length
        work_end = prev_session["work"].start_time + datetime.timedelta(minutes=self.work_length)
        latest_lunch_start = self.start_time.replace(hour=11, minute=59)
        if work_end > latest_lunch_start:
            work_diff_minutes = (latest_lunch_start - work_end).total_seconds() / 60
            work_length = self.work_length - abs(work_diff_minutes)

        session["work"] = Period("work", prev_session["rest"].end_time, work_length)


#TODO turn into .exe so I can run it in a windows commandline
if __name__ == "__main__":
    timer = WorkTimer(args)