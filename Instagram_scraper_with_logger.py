# Imports
from time import sleep, time
import os
import json
from instaloader import FrozenNodeIterator
from instaloader.exceptions import ConnectionException, LoginRequiredException, ProfileNotExistsException
import instaloader
from SupportingFiles.GSheet import GSheet
from loguru import logger

# Get Inputs from the user for scraping details
STARTING_INDEX = int(input("Please enter starting index: "))
ENDING_INDEX = int(input("Please enter starting index: "))
BATCHSIZE = int(input("Please enter batch size: "))
logger.add(f"logs/file_{STARTING_INDEX}_{ENDING_INDEX}_{time()}.log")
logger.info("Starting instagram Scraping!")

gsheet = GSheet()
five_k_profiles = gsheet.get_5kprofiles("Instagram5k")

@logger.catch()
def download_JSON(USERNAME,i):
    # Initialize
    L = instaloader.Instaloader(download_comments =True)
    downloadedSuccesfully = False
    post_iterator = instaloader.Profile.from_username(L.context, USERNAME).get_posts()
    gsheet.updateValue(i,'I',post_iterator.count)
    logger.info(f'{i} {USERNAME} has {post_iterator.count}')

    # Create profile folder
    file_exists = os.path.isdir(f'JSONPosts/{i}_{USERNAME}')
    if not file_exists:
        os.mkdir(f'JSONPosts/{i}_{USERNAME}')

    # Start scraping
    with instaloader.resumable_iteration(
        context=L.context,
        iterator=post_iterator,
        load=lambda _, path: FrozenNodeIterator(**json.load(open(path))),
        save=lambda fni, path: json.dump(fni._asdict(), open(path, 'w')),
        format_path=lambda magic: "JSONPosts/{}_{}/resume_info_{}.json".format(i,USERNAME,magic)
        ) as (is_resuming, start_index):
            try:
                stored_index=start_index
                for post in post_iterator:
                    if(start_index-stored_index<(BatchSize+1)):
                        # if(start_index%20==0):
                        logger.info(f"{i} User Downloading {start_index} post, dated {post.date}")
                        instaloader.save_structure_to_file(post, f"JSONPosts/{i}_{USERNAME}/{USERNAME}_{start_index}")
                        start_index+=1
                    else:
                        logger.info(f"{BatchSize} post completed. Stoping download for {i} {USERNAME} User at {start_index} index.")
                        gsheet.updateValue(i,'J',start_index)
                        raise KeyboardInterrupt
                if((start_index)<post_iterator.count and (start_index-stored_index)<5):
                    logger.warning(f"Posts not completely downloaded: start_index={start_index} Post_count={post_iterator.count} difference={post_iterator.count-start_index}")
                    gsheet.updateValue(i,'J',start_index)
                    raise KeyboardInterrupt
                else:
                    logger.success(f"{USERNAME} completed with start_index={start_index} Post_count={post_iterator.count}")
                    downloadedSuccesfully= True
                    gsheet.updateValue(i,'J',start_index)
                    return downloadedSuccesfully
            except ConnectionException:
                logger.warning(f"401 Error while downloading {USERNAME} profile stopped at {start_index} post")
                gsheet.updateValue(i,'J',start_index)
                raise KeyboardInterrupt
            except LoginRequiredException:
                logger.warning(f"Login required exception caught. Stopping {USERNAME} at {start_index} post")
                gsheet.updateValue(i,'J',start_index)
                raise KeyboardInterrupt
            except ProfileNotExistsException:
                logger.warning(f"{USERNAME} Does not exist, please recheck once")
                gsheet.updateValue(i,'J',start_index)
                gsheet.updateValue(i,'G',100)
                raise KeyboardInterrupt

# Scrape for specified batch size
for i in range(STARTING_INDEX,ENDING_INDEX):
    profile=five_k_profiles[i]
    download_status = gsheet.getValue(i,'G')
    if int(download_status)==1 or int(download_status)==100:
        logger.info(f"Skipping {i} {profile}")
    elif int(download_status)!=1:
        try:
            JSONOutput = download_JSON(profile,i)
        except KeyboardInterrupt:
            logger.warning(f"Keybord exception raised for {i} {profile}")
            gsheet.updateValue(i,'G',99)
            JSONOutput=False
        except LoginRequiredException:
            logger.warning(f'Login required on {i} {profile} ')
            gsheet.updateValue(i,'G',99)
            JSONOutput=False
        except ProfileNotExistsException:
            logger.warning(f'Profile {i} {profile}, does not exist. Please recheck')
            gsheet.updateValue(i,'G',100)
            JSONOutput=False
        except ConnectionException:
            logger.warning(f'401 Error while downloading {i} {profile} profile')
            gsheet.updateValue(i,'G',99)
            JSONOutput=False
        except Exception as e:
            logger.exception(e)
        finally:
            logger.debug(f'JSONOutput status:{JSONOutput} for {i} {profile} profile')
            if(JSONOutput):
                gsheet.updateValue(i,'G',1)
            else:
                gsheet.updateValue(i,'G',99)
            sleep_time=0.0001*i
            sleep(sleep_time)
    logger.info("One loop completed")
    