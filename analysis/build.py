import logging
import threading
import time

class Task:
    def validate(self):
        raise NotImplementedError()

    def perform(self):
        raise NotImplementedError()

    def cleanup(self):
        pass

class Build:
    def __init__(self):
        self.tasks = {}

    def add_task(self, name, task, dependencies):
        if name in self.tasks:
            raise RuntimeError('Task "%s" is already registered' % name)

        self.tasks[name] = (task, dependencies)

    def _build_queue(self, name):
        unvisited = [name]
        queue = []

        while len(unvisited) > 0:
            name = unvisited.pop()
            dependencies = self.tasks[name][1][:]
            queue.append(name)

            for d in dependencies:
                if d in queue:
                    raise RuntimeError('Circular reference between "%s" and "%s"' % (name, d))

                if not d in unvisited:
                    unvisited.insert(0, d)

        return list(reversed(queue))

    def build(self, name, nthreads):
        if not name in self.tasks:
            raise RuntimeError('Task "%s" is not registered' % name)

        logging.info('Starting build for "%s"' % name)

        pending = self._build_queue(name)
        finished = set()

        for name in pending:
            if self.tasks[name][0].validate() and finished.issuperset(set(self.tasks[name][1])):
                finished.add(name)

        for name in finished:
            pending.remove(name)

        logging.info('Skipping %d tasks.' % len(finished))

        threads = {}

        while len(pending) > 0 or len(threads) > 0:
            dead = [name for name in threads if not threads[name].is_alive()]

            for name in dead:
                task = self.tasks[name][0]
                finished.add(name)
                del threads[name]

                if task.validate():
                    logging.info('Done performing task "%s"!' % name)
                else:
                    logging.error('Task "%s" failed!' % name)
                    return False

            if len(pending) > 0 and len(threads) < nthreads:
                available = [name for name in pending if finished.issuperset(set(self.tasks[name][1]))]

                if len(available) > 0:
                    name = available.pop()
                    pending.remove(name)

                    threads[name] = threading.Thread(target = self.tasks[name][0].perform)
                    threads[name].daemon = True

                    logging.info('Performing task "%s" ...' % name)
                    threads[name].start()

            if len(pending) > 0 and len(threads) == 0:
                time.sleep(1.0)

        return True

class PrintTask(Task):
    def __init__(self, message, sleep, initial):
        self.message = message
        self.sleep = sleep
        self.status = initial

    def validate(self):
        return self.status

    def perform(self):
        time.sleep(self.sleep)
        print("Message: %s" % self.message)
        self.status = True

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    build = Build()

    build.add_task('uvw', PrintTask('uvw', 0.0, True), [])
    build.add_task('abc', PrintTask('abc', 0.0, True), ['def'])
    build.add_task('def', PrintTask('def', 2.0, True), ['ghi', 'uvw'])
    build.add_task('ghi', PrintTask('ghi', 0.0, True), ['uvw'])

    build.build('abc', 4)
