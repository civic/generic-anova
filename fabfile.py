# coding: utf-8

from fabric.api import *
from fabric.contrib.files import *

env.use_ssh_config =True

def webpack():
    with lcd("web"):
        local("npm run build")

def sync():
    local("rsync -a -e ssh generic_anova setup.py static pi-zero:.")
    sudo("supervisorctl restart all");
