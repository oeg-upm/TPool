import threading
import logging


class Pool:
    """
    This is a thread pool to extend the functionality of ThreadPool in Python2
    """

    def __init__(self, max_num_of_threads, func, params_list, logger=None):
        """
        :param max_num_of_threads:
        :param func:
        :param params_list:
        :param logger:
        """
        if len(params_list) < max_num_of_threads:
            max_num_of_threads = len(params_list)

        self.max_num_of_thread = max_num_of_threads
        self.func = func
        self.param_list = params_list

        self.threads = []

        if logger is None:
            logger = logging.getLogger(__name__)
            handler = logging.NullHandler()
            logger.addHandler(handler)
        self.logger = logger

    def run(self):
        """
        To run the pool
        :return:
        """
        active = 0
        remaining = len(self.param_list)

        while active > 0 or remaining > 0:
            to_be_removed = []
            # Get threads to be removed
            for idx, thread in enumerate(self.threads):
                if not thread.is_alive():
                    to_be_removed.append(idx)

            for i in to_be_removed[::-1]:  # go in a descending order
                self.threads[i].join()
                del self.threads[i]

            remaining = len(self.param_list)
            available_slots = self.max_num_of_thread - active
            available_slots = min(available_slots, remaining)

            for slot in range(available_slots):
                params = self.param_list[-1]
                th = threading.Thread(target=self.func, args=params)
                del self.param_list[-1]
                th.start()
                self.threads.append(th)

            remaining = len(self.param_list)
            active = len(self.threads)

            if available_slots > 0 or active > 0:
                self.logger.debug("available slots: "+str(available_slots))
                self.logger.debug("active: "+str(active))
                self.logger.debug("remaining: "+str(remaining))


