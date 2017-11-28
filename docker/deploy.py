# -*- coding:utf-8 -*-
import os

os.system("docker build -f pf.dockerfile -t cnaafhvk/proxy-factory:latest .")
os.system("docker push cnaafhvk/proxy-factory")
