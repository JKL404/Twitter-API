from datetime import date, timedelta
import os


async def remove_old_files():
    # function to remove old files
    print('delete mode')
    my_dir = "static/downloads/"
    for fname in os.listdir(my_dir):
        for day in range(2, 31):
            old_filename = date.today() - timedelta(days=day)
            if fname.startswith(str(old_filename)):
                os.remove(os.path.join(my_dir, fname))
