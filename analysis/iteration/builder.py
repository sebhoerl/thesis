import logging
import threading
import time
import sqlite3
import traceback

class Task:
    def validate(self):
        raise NotImplementedError()

    def perform(self):
        raise NotImplementedError()

    def cleanup(self):
        pass

class Builder:
    def __init__(self):
        self.tasks = {}
        self.logger = logging.getLogger('Builder')

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

    def _validate(self, task):
        try:
            return task.validate()
        except Exception as e:
            traceback.print_exc()
            return False

    def _perform(self, task):
        try:
            return task.perform()
        except Exception as e:
            traceback.print_exc()
            return False

    def build(self, name, nthreads):
        if not name in self.tasks:
            raise RuntimeError('Task "%s" is not registered' % name)

        self.logger.info('Starting build for "%s"' % name)

        pending = self._build_queue(name)
        finished = set()

        for name in pending:
            if self._validate(self.tasks[name][0]) and finished.issuperset(set(self.tasks[name][1])):
                finished.add(name)

        for name in finished:
            pending.remove(name)

        self.logger.info('Skipping %d tasks.' % len(finished))

        threads = {}
        failures = set()

        while len(pending) > 0 or len(threads) > 0:
            dead = [name for name in threads if not threads[name].is_alive()]

            for name in dead:
                task = self.tasks[name][0]
                finished.add(name)
                del threads[name]

                if self._validate(task):
                    self.logger.info('Done performing task "%s"!' % name)
                else:
                    self.logger.error('Task "%s" failed!' % name)
                    failures.add(name)

            if len(pending) > 0 and len(threads) < nthreads:
                available = [name for name in pending if finished.issuperset(set(self.tasks[name][1]))]

                if len(available) > 0:
                    name = available.pop()
                    pending.remove(name)

                    failed_deps = failures.intersection(set(self.tasks[name][1]))
                    if len(failed_deps) > 0:
                        self.logger.info('Skipping "%s" due to failed dependency "%s"' % (name, ','.join(failed_deps)))
                        finished.add(name)
                        failures.add(name)
                    else:
                        threads[name] = threading.Thread(target = self._perform, args = (self.tasks[name][0],))
                        threads[name].daemon = True

                        logging.info('Performing task "%s" ...' % name)
                        threads[name].start()

            if len(pending) > 0 and len(threads) == nthreads:
                time.sleep(1.0)

        return True
