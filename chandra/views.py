from django.contrib.auth import login, authenticate,logout
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .forms import UserForm
import base64
from io import BytesIO
import pickle
from skimage.transform import resize, SimilarityTransform, warp
import numpy as np
from skimage import io as skio





from sklearn.externals import joblib
model = joblib.load('./chandra/static/filename.pkl')

def index(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request,user)
                return render(request, 'chandra/index.html')
            else:
                return render(request, 'chandra/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'chandra/login.html', {'error_message': 'Invalid login'})
    else:
        if not request.user.is_authenticated:
         return render(request,'chandra/login.html')
        else:
             return render(request, 'chandra/index.html')



def logout_user(request):
    return render(request, 'chandra/login.html')


def login_user(request):
    return render(request, 'chandra/login.html')


def register(request):
    form=UserForm(request.POST or None)
    if form.is_valid():
        user=form.save(commit=False)
        username=form.cleaned_data['username']
        password=form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user=authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request,user)
                return render(request, 'chandra/index.html')
    context = {
        "form": form,
    }
    return render(request, 'chandra/register.html',context)


def about(request):
    return render(request, 'chandra/about.html')


def recognize(request):

    return render(request, 'chandra/recognize.html')


def digit(request):
    if request.is_ajax():
        if request.method == 'POST':
            data = str(request.body)
           # print('!!!!!',data,'!!!!!1')
            data = data[34:]
            #print(data)


            img = skio.imread(BytesIO(base64.b64decode(data)))[:, :, 3]
            #print(img.shape,'  gg')
            img = make_mnist(img)
            img=img.reshape(1,-1).astype('float32')

            #print('!!!!',img.shape,'!!!!!!!!!!!!!!!')

           # img = img / 255

           # print('!!!image data= ', img,'\n\n')
            #print(type(img))

            number = model.predict(img[0:1])

            return HttpResponse(str(number))
           # return render(request, 'chandra/recognize.html')



def make_mnist(img):
    # Padding
    R, C = img.shape
    pad = 450
    tmp = np.zeros((R + 2 * pad, C + 2 * pad)).astype(int)
    tmp[pad:pad + R, pad:pad + C] = img
    # Computing the bounding box
    nonzY, nonzX = np.where(tmp)
    ly, lx = nonzY.min(), nonzX.min()
    ry, rx = nonzY.max(), nonzX.max()

    if (rx - lx) < (ry - ly):
        rx = lx + (ry - ly)

    if (rx - lx) > (ry - ly):
        ry = ly + (rx - lx)

    img = resize(tmp[ly:ry, lx:rx].astype(float), (20, 20))
    tmp=resize(tmp[ly:ry, lx:rx].astype(float), (28, 28))
    #Now inserting the 20x20 image
    tmp = np.zeros((28, 28))
    tmp[0:20, 0:20] = img

    # Calculating translation

    Y, X = np.where(tmp)
    R, C = tmp.shape

    tsy, tsx = np.round(R / 2 - Y.mean()), np.round(C / 2 - X.mean())
    #Moving the digit
    tf = SimilarityTransform(translation=(-tsx, -tsy))
    tmp = warp(tmp, tf)
    return np.round(tmp).astype(int)

