from django.shortcuts import render
from .models import Tweet
from .forms import TweetForm , UserRegistrationForm
from django.shortcuts import get_object_or_404 , redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Q 


# Create your views here.

def index(request):
    return render(request, 'index.html')


#To list all tweets
def tweet_list(request):
    tweets = Tweet.objects.all().order_by('-created_at')
    return render(request, 'tweet_list.html', {'tweets': tweets}) 


#To create a tweet
@login_required
def tweet_create(request):
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet =form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    
    else:
        form = TweetForm()
    return render(request, 'tweet_form.html', {'form': form})

#To edit a tweet
@login_required
def tweet_edit(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm(instance=tweet)
    return render(request, 'tweet_form.html', {'form': form})

#To delete a tweet
@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method =='POST':
        tweet = tweet.delete()
        return redirect('tweet_list')
    return render(request, 'tweet_delete.html', {'tweet': tweet})

def register(request):
    if request.method =='POST':
       form = UserRegistrationForm(request.POST)
       if form.is_valid():
          user = form.save(commit=False)
          user.set_password(form.cleaned_data['password1'])
          user.save()
          login(request, user)
          return redirect('tweet_list') 
    else:
        form = UserRegistrationForm()      
    return render(request, 'registration/register.html', {'form': form})



def search_tweets(request):
    # 1. Get the query string 'q' from the URL parameters
    query = request.GET.get('q')
    
    # Start with all tweets, just in case the query is empty
    tweets = Tweet.objects.all()

    if query:
        # 2. Use Q objects to perform a case-insensitive OR lookup
        # This will filter tweets where the content OR the user matches the query
        tweets = tweets.filter(
            Q(text__icontains=query) |   # search in the post/tweet content
            Q(user__username__icontains=query)        # search in the user/author name
        ).distinct() 

    context = {
        'tweets': tweets,
        'query': query, 
    }
    
    # 3. Render the main page template with the filtered list
    # Assuming your main page template is named 'tweet_page.html'
    return render(request, 'tweet_list.html', context)


