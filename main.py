import datetime
import time
import search_download as search
import combine


start_time = time.time()
search.search_and_download()
print('Combining all videos')
combine.combineAll()
end_time = time.time()
total_time = end_time - start_time
convert = str(datetime.timedelta(seconds=total_time))
print('Total time spent: ' + "%s" % str(convert).split('.')[0])
