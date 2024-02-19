# Imports
import pandas as pd
from time import sleep
import os
import json
import random
from instaloader import FrozenNodeIterator
from instaloader.exceptions import ConnectionException, LoginRequiredException
import instaloader


# Get proxies and profiles
with open("./smartproxy_list.txt","r") as f:
    proxies = f.read().split("\n")
proxy_counter = 0
JSONOutput = False
contn='y'
df = pd.read_csv('5kprofile.csv')

rootfolder = os.path.isdir('JSONPosts')
if not rootfolder:
        os.mkdir(f'JSONPosts')

# Read profiles        
five_k_profiles = [x[1:] for x in df["Profile"]]
df['JSON Downloaded'] = df['JSON Downloaded'].fillna(0)

def download_JSON(USERNAME, proxy):
    # Initialize
    L = instaloader.Instaloader(download_comments =True)
    proxies = {
    "http": proxy,
    "https": proxy,
    }
    downloadedSuccesfully = False
    L.context._session.proxies = proxies
    post_iterator = instaloader.Profile.from_username(L.context, USERNAME).get_posts()
    print(f'{USERNAME} has {post_iterator.count}')

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
                    if(start_index-stored_index<501):
                        if(start_index%10==0):
                            print(f"{i} User Downloading {start_index} post, dated {post.date}")
                        instaloader.save_structure_to_file(post, f"JSONPosts/{i}_{USERNAME}/{USERNAME}_{start_index}")
                        start_index+=1
                    else:
                        print(f"Stoping download for {i} User {USERNAME} at {start_index} index")
                        sleep(0.5)
                        raise KeyboardInterrupt
                print(f"{USERNAME} completed")
                downloadedSuccesfully= True
                return downloadedSuccesfully
            except ConnectionException:
                print(f"401 Error while downloading {USERNAME} profile stopped at {start_index} post")
                raise KeyboardInterrupt
            except LoginRequiredException:
                print("Login required exception caught. Stopping "+str(profile))
                raise KeyboardInterrupt

# Iterate over profiles
while True:
    i=random.randrange(500, 5000)
    profile=five_k_profiles[i]
    if int(df["JSON Downloaded"][i])==1:
        print("Skipping "+profile)
    elif int(df["JSON Downloaded"][i])!=1:
        try:
            JSONOutput = download_JSON(profile,proxies[proxy_counter])
        except KeyboardInterrupt:
            print("Keybord exception raised")
            if(contn!='y'):
                break
        finally:
            if(JSONOutput):
                df.loc[i, ('JSON Downloaded')] = 1
                df.to_csv("5kprofile.csv", index=False)
                print("CSV Updated")
            else:
                proxy_counter += 1
                proxy_counter = proxy_counter % len(proxies) 
                try:
                    JSONOutput = download_JSON(profile,proxies[proxy_counter])
                except KeyboardInterrupt:
                    print("Keybord exception raised")
                    # contn = input("Do you want to continue?").lower()
                    if(contn!='y'):
                        break
                except LoginRequiredException:
                    print('Login required on '+profile+' , please login manually and rerun the')
                finally:
                    if(JSONOutput):
                        df.loc[i, ('JSON Downloaded')]=1
                        df.to_csv("5kprofile.csv", index=False)
                        print("CSV Updated")
                    else:
                        df.loc[i, ('JSON Downloaded')]=99
                        proxy_counter += 1
            sleep_time=0.0001*i
            print(f'sleeping for {sleep_time} sec')
            sleep(sleep_time)
    if i%10==0 and i!=0:
        df.to_csv("5kprofile.csv", index=False) 

