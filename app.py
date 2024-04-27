from geminibot_utils import *
import random
import sys
from apscheduler.schedulers.blocking import BlockingScheduler


if __name__ == "__main__":
    random.seed()
    try:
        task()
        scheduler = BlockingScheduler()
        scheduler.add_job(task, trigger='interval', minutes=random.randint(1, interval))
        scheduler.start()
    except BaseException as e:
        import traceback
        traceback.print_exc()
        logger.error(e)
        logger.info("Saving ignored content_id...")
        if os.path.exists(pickle_path):
            os.replace(pickle_path, archived_pickle_path)
        with open(pickle_path, "wb") as pickleFile:
            pickle.dump(ignored_content, pickleFile)
        logger.info("Completed.")
        sys.exit()

