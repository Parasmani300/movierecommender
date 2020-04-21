from django.shortcuts import render
from recommender.forms import SearchBar
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
import pandas as pd;
import os
from . import movieDetails
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from recommender.forms import UserForm,UserProfileInfoForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth import authenticate,login,logout

#for fetching user details
from recommender.models import Profile
# Create your views here.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_DIR = os.path.join(BASE_DIR,'static')
C_FILE = os.path.join(CSV_FILE_DIR,'movie_dataset.csv')
df = pd.read_csv(C_FILE)
###### helper functions. Use them when needed #######
def get_title_from_index(index):
	return df[df.index == index]["title"].values[0]

def get_index_from_title(title):
	return df[df.title == title]["index"].values[0]
##################################################

def get_director_from_title(title):
    return df[df.title == title]["director"].values[0]

def get_rel_Date_from_title(title):
    return df[df.title == title]["release_date"].values[0]

def get_overview_from_title(title):
    return df[df.title == title]["overview"].values[0]

def get_budget_from_title(title):
    return df[df.title == title]["budget"].values[0]

def get_homepage_from_title(title):
    return df[df.title == title]["homepage"].values[0]


##Step 1: Read CSV File

#print df.columns
##Step 2: Select Features

features = ['keywords','cast','genres','director']
##Step 3: Create a column in DF which combines all selected features
for feature in features:
	df[feature] = df[feature].fillna('')

def combine_features(row):
	try:
		return row['keywords'] +" "+row['cast']+" "+row["genres"]+" "+row["director"]
	except:
		print("Error:", row)	

df["combined_features"] = df.apply(combine_features,axis=1)

#print "Combined Features:", df["combined_features"].head()

##Step 4: Create count matrix from this new combined column
cv = CountVectorizer()

count_matrix = cv.fit_transform(df["combined_features"])

##Step 5: Compute the Cosine Similarity based on the count_matrix
cosine_sim = cosine_similarity(count_matrix) 
#movie_user_likes = "Avatar"

## Step 6: Get index of this movie from its title
def user_likes(movie_user_likes):
    movie_index = get_index_from_title(movie_user_likes)
    similar_movies =  list(enumerate(cosine_sim[movie_index]))
    ## Step 7: Get a list of similar movies in descending order of similarity score
    sorted_similar_movies = sorted(similar_movies,key=lambda x:x[1],reverse=True)
    ## Step 8: Print titles of first 50 movies
    i=0
    s1=''
    lis = []
    for element in sorted_similar_movies:
        s=get_title_from_index(element[0])
         #fetching movie details
        try:
            title = s
            relYear = get_rel_Date_from_title(s)
            directorName = get_director_from_title(s)
            overview = get_overview_from_title(s)
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.relpath(__file__)))
            STATIC_DIR = os.path.join(BASE_DIR,"static")
            if get_index_from_title(s) in [37,66,442,797,999,1019,1190,1616,1687,1790,1808,2097,2197,2365,2531,2735,1429,2756,3207,3208,3245,3278,3371,3446,3751,3853,4029,4055,4075,4366,4729]:
                img = str(get_index_from_title(title))+".jpg"
            else:
                img = title + ".jpg"
            coverurl = os.path.join(STATIC_DIR,'image')
            coverurl = os.path.join(coverurl,img)
            movieAll = movieDetails.movieDetails(title,relYear,directorName,coverurl,overview)
            lis.append(movieAll)
        except IndexError:
            pass 
        s1+=s+','
        i=i+1
        if i>5:
            break
    return lis

def top20movies():
     lis = []
     for x in range(20):
         index = x
         movie = get_title_from_index(index)
         title = movie
         relYear = get_rel_Date_from_title(title)
         directorName = get_director_from_title(title)
         overview = get_overview_from_title(title)
         try:
             BASE_DIR = os.path.dirname(os.path.dirname(os.path.relpath(__file__)))
             STATIC_DIR = os.path.join(BASE_DIR,"static")
             img = title+".jpg"
             coverurl = os.path.join(STATIC_DIR,'image')
             coverurl = os.path.join(coverurl,img)
             #print(coverurl)
             movieAll = movieDetails.movieDetails(title,relYear,directorName,coverurl,overview)
             lis.append(movieAll)
         except IndexError:
             pass
     return lis
movies = user_likes('Avatar')
#for movie in top20movies():
   # print(movie.title)


@login_required
def special(request):
    # Remember to also set login url in settings.py!
    # LOGIN_URL = '/basic_app/user_login/'
    return HttpResponse("You are logged in. Nice!")

@login_required
def user_logout(request):
    # Log out the user.
    logout(request)
    # Return to homepage.
    return HttpResponseRedirect(reverse('index'))

def common_movie(movie,movie1_list):
    for m in movie1_list:
        if m.title == movie.title:
            return movie1_list
    movie1_list.append(movie)
    return movie1_list

def index(request):
    msg = ""
    user_profile = Profile.objects.all()
    if request.method == "POST":
        form = SearchBar(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            try:
                movies = user_likes(search)
            except IndexError:
                if request.user.is_authenticated:
                    msg = "No related movies"
                    movie1 = request.user.profile.movie1
                    movie2 = request.user.profile.movie2
                    movie3 = request.user.profile.movie3
                    movie4 = request.user.profile.movie4

                    movie1_list = user_likes(movie1)
                    movie2_list = user_likes(movie2)
                    movie3_list = user_likes(movie3)
                    movie4_list = user_likes(movie4)

                    for movie in movie2_list:
                        movie1_list = common_movie(movie,movie1_list)
                    for movie in movie3_list:
                        movie1_list = common_movie(movie,movie1_list)
                    for movie in movie4_list:
                        movie1_list = common_movie(movie,movie1_list)

                    movies = movie1_list
                else:
                    movies = top20movies()
                    msg = "No related movies"
    else:
        form = SearchBar()
        search = ""
        if request.user.is_authenticated:
            movie1 = request.user.profile.movie1
            movie2 = request.user.profile.movie2
            movie3 = request.user.profile.movie3
            movie4 = request.user.profile.movie4

            movie1_list = user_likes(movie1)
            movie2_list = user_likes(movie2)
            movie3_list = user_likes(movie3)
            movie4_list = user_likes(movie4)

            for movie in movie2_list:
                movie1_list = common_movie(movie,movie1_list)
            for movie in movie3_list:
                movie1_list = common_movie(movie,movie1_list)
            for movie in movie4_list:
                movie1_list = common_movie(movie,movie1_list)

            movies = movie1_list
        else:
            movies = top20movies()
    return render(request,'index.html',{'form':form,'movies':movies,'msg':msg,'user_profile':user_profile})
    

def register(request):

    registered = False

    if request.method == 'POST':

        # Get info from "both" forms
        # It appears as one form to the user on the .html page
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)

        # Check to see both forms are valid
        if user_form.is_valid() and profile_form.is_valid():

            # Save User Form to Database
            user = user_form.save()

            # Hash the password
            user.set_password(user.password)

            # Update with Hashed password
            user.save()

            # Now we deal with the extra info!

            # Can't commit yet because we still need to manipulate
            profile = profile_form.save(commit=False)

            # Set One to One relationship between
            # UserForm and UserProfileInfoForm
            profile.user = user

            # Check if they provided a profile picture
            if 'profile_pic' in request.FILES:
                print('found it')
                # If yes, then grab it from the POST form reply
                profile.profile_pic = request.FILES['profile_pic']

            # Now save model
            profile.save()

            # Registration Successful!
            registered = True

        else:
            # One of the forms was invalid if this else gets called.
            print(user_form.errors,profile_form.errors)

    else:
        # Was not an HTTP post so we just render the forms as blank.
        user_form = UserForm()
        profile_form = UserProfileInfoForm()

    # This is the render and context dictionary to feed
    # back to the registration.html file page.
    return render(request,'registration.html',
                          {'user_form':user_form,
                           'profile_form':profile_form,
                           'registered':registered})



def user_login(request):

    if request.method == 'POST':
        # First get the username and password supplied
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Django's built-in authentication function:
        user = authenticate(username=username, password=password)

        # If we have a user
        if user:
            #Check it the account is active
            if user.is_active:
                # Log the user in.
                login(request,user)
                # Send the user back to some page.
                # In this case their homepage.
                return HttpResponseRedirect(reverse('index'))
            else:
                # If account is not active:
                return HttpResponse("Your account is not active.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            return HttpResponseRedirect(reverse('index'))

    else:
        #Nothing has been provided for username or password.
        return render(request, 'index.html', {})


################################# This is a movie details section #####################################################
def movie_details(request,value):
    title = value
    director = get_director_from_title(title)
    year = get_rel_Date_from_title(title)
    overview = get_overview_from_title(title)
    homepage = get_homepage_from_title(title)
    img = title+".jpg"
    coverurl = img

    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        if profile.replacer == 1:
            profile.movie1 = title
        elif profile.replacer == 2:
            profile.movie2 = title
        elif profile.replacer == 3:
            profile.movie3 = title
        else:
            profile.movie4 = title
        profile.replacer = (profile.replacer + 1)%4
        if profile.replacer == 0:
            profile.replacer = 4
        profile.save()

    movie = movieDetails.movieDetails(title,year,director,coverurl,overview)
    similar_movies = user_likes(title)
    return render(request,'movie_details.html',{'movie':movie,'similar_movies':similar_movies})