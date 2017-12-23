from bs4 import BeautifulSoup as bs
import os
import threading
import requests

host = "http://index-of.co.uk/"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

fully_retrieved_dir = []

def main():
    try:
        site_dir_list = get_site_dir_list() #get the directory link from the site to cmpre incase there is new
        if not os.path.isfile(os.getcwd()+"/retrieved_dir.dmd"):
            with open(os.getcwd()+"/retrieved_dir.dmd", "w") as f:
                pass
        with open(os.getcwd()+"/retrieved_dir.dmd", "r") as f:
            dirs = f.readlines()
        if dirs != []:
            for dir in dirs:
                dir = dir.strip("\n")
                if dir in site_dir_list:
                    site_dir_list.remove(dir)
        create_threads(site_dir_list[0])
    except Exception:
        save()

def create_threads(dir_links):
    try:
        print("called")
        while dir_links != []:
            threads_list = []
            for _ in range(10):
                if dir_links != []:
                    dir_link = dir_links[-1]
                    print dir_link
                    new_thread = threading.Thread(target=get_links, args=(dir_link))
                    threads_list.append(new_thread)
                    print("trying to remove %s \n"%dir_links[-1])
                    dir_links.remove(dir_links[-1])
                    print("new length of list is %d \n"%len(dir_links))
                else:
                    print("Exhausted directory links")
            if threads_list != []: #confirms that threads list is not empty
                for thread in threads_list:
                    thread.start()
                for thread in threads_list:
                    thread.join()
            else:
                print("Exhausted Threads list")
            save()
    except Exception:
        save()


def get_links(dir_link):
    try:
        print("get links entered")
        with requests.Session() as s:
            page = s.get(host+"/"+dir_link, headers=headers) #open the page of the current directory
        if not os.path.isdir(os.getcwd()+"/"+dir_link): #check if the directory has not been created
            os.mkdir(os.getcwd()+"/"+dir_link)  # create the directory
        files_link = get_files_link(page.content) # call the function that retrieve and returns the links
        print("links obtained...")
        with requests.Session() as s:
            for link in files_link:
                file_name = validate_filename(link)
                if not os.path.isfile(os.getcwd()+"/"+dir_link+file_name):
                    print("trying to retrieve %s from %s \n"%(file_name, dir_link))
                    file_get = s.get(host+"/"+dir_link+link, headers=headers)
                    with open(os.getcwd()+"/"+dir_link+file_name, "wb") as f:
                        f.write(file_get.content)
                    print("Retrieved %s \n"%file_name)
            fully_retrieved_dir.append(dir_link)
    except Exception:
        save()


def validate_filename(link):
    try:
        name = link.replace("%20", "_")
        return name
    except Exception:
        save()


def get_files_link(page):
    try:
        links = []
        soup = bs(str(page), "html.parser")
        a_tags = soup.find_all("a")
        for a in a_tags:
            link = a["href"]
            if link_is_file(link):
                links.append(link)
        return links
    except Exception:
        save()


def link_is_file(link):
    try:
        if link[:4] == "http":
            return False
        elif link[-1] == "/":
            return False
        elif not link[0].isupper():
            return False
        else:
            return True
    except Exception:
        save()


#this function retrieve the link of dirs from the site
def get_site_dir_list():
    try:
        links = []
        with requests.Session() as s:
            open_homepage = s.get(host, headers=headers) #opening the homepage of the site
        homepage = open_homepage.content # this is trivial
        soup = bs(str(homepage), "html.parser")
        a_tags = soup.find_all("a")
        all_links = []
        for a in a_tags:
            link = a["href"] #extracting the link text with bs
            all_links.append(link)
        for link in all_links:
            if is_link_dir(link):
                links.append(link)
        return links
    except Exception:
        save()

#this function is called to save the name of directories that have been retrieved
def save():
    with open(os.getcwd()+"/retrieved_dir.dmd", "a") as f:
        if fully_retrieved_dir != []:
            for dir in fully_retrieved_dir:
                f.write(dir+"\n")


# performs simple checks if don't get this too, this code is not for u
def is_link_dir(link):
    try:
        if link[:4] == "http":
            return False
        elif link[-1] != "/":
            return False
        elif not link[0].isupper():
            return False
        else:
            return True
    except Exception:
        save()


if __name__=="__main__":
    main()
