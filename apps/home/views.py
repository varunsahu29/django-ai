# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.utils.encoding import smart_str
import csv
import os,os.path
from django.conf import settings
@login_required(login_url="/login/")
def index(request):
    context={}
    notes=["Click on CvInput",
            "Enter project name",
            "Upload the file",
            "Select the column",]
    context['notes']=notes
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]
        print(load_template,request.method)
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
        if load_template == 'cvInput.html':
            if request.method == 'POST'  :
                if request.POST.get("done")=="":
                    username=request.user.username
                    name=request.POST['name']
                    upload=request.FILES['upload']
                    fss=FileSystemStorage()
                    fss.location+="/{}/{}".format(username,name)
                    file=fss.save("{}.csv".format(name),upload)
                    import pandas as pd
                    df = pd.read_csv(fss.open("{}.csv".format(name)))
                    context['headers']=list(df.columns)
                    context['file_name']=name
                    print(name)
                    return HttpResponse(loader.get_template('home/cvDisplay.html').render(context,request))
                else:
                    select=""
                    file_name=""
                    for key in request.POST.dict():
                        if(key!="csrfmiddlewaretoken"):
                            if key=="__":
                                file_name=request.POST[key]
                            else:
                                select=key
                    fss=FileSystemStorage()
                    fss.location+="/{}/{}".format(request.user.username,file_name)
                    import pandas as pd
                    from sklearn.model_selection import train_test_split
                    from supervised.automl import AutoML
                    df = pd.read_csv(fss.open("{}.csv".format(file_name)))
                    Y=df[select]
                    X=df.drop(select,axis=1)
                    from supervised.preprocessing.eda import EDA
                    path = settings.MEDIA_ROOT
                    extra="/{}/{}/{}".format(request.user.username,file_name,select)
                    path+=extra
                    EDA.extensive_eda(X,Y,save_path=path)
                    imgs = []
                    valid_images = [".jpg",".gif",".png",".tga"]
                    for f in os.listdir(path):
                        ext = os.path.splitext(f)[1]
                        if(ext=='.png'):
                            imgs.append([f[:-4],'media'+extra+'/'+f])
                    print(imgs)
                    context['imgs']=imgs
                    return HttpResponse(loader.get_template('home/cvRunModel.html').render(context,request))   
            else:   
                html_template = loader.get_template('home/' + load_template)
                return HttpResponse(html_template.render(context, request))
        elif load_template == 'cvRunModel':
            if request.method == 'POST'  :
                return HttpResponse("POST")
            else:   
                # return HttpResponse("{}".format(request.method))
                html_template = loader.get_template('home/' + load_template)
                return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
