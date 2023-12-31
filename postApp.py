from flask import Blueprint, jsonify, Flask, request, render_template, session, redirect, send_from_directory, url_for
from werkzeug.utils import secure_filename
import re

import os
from model.community import *
from model.post import *
from model.user import *
from model.comment import *
from model.like import *

app = Flask(__name__)
post_blueprint = Blueprint('post', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_session():
    username = session.get("username")
    communityName = session.get("location")
   
    if not username:
        return False, jsonify({'status': 'failed', 'message': 'Please log in firstly'}), 401

    return True, (username, communityName)

#Route for Creating the posts
@post_blueprint.route("/createPost", methods=["GET", 'POST'])
def createPost():
    if request.method == 'POST':
        user_check, user_data = check_session()
   
        if not user_check:
            return user_data
        username, communityName = user_data
        user_id = get_user_id_by_username(username)['id']
       
        communityId = get_community_id_by_communityName(communityName)['id']
       
        file_path = os.path.join(os.path.dirname(__file__), 'en.txt')  # Path to the curse word dictionary
       
        title = request.form.get("title")
        #checking if curse words are present in the Title
        result_title = auto_moderator(file_path, title)
        if result_title:
            return """
            <script>
                alert("Title contains a curse word. Please choose another title.");
                window.location.href = '/post/createPost';  // Redirect back to the createPost page
            </script>
            """

        content = request.form.get("content")
        #checking if curse words are present in the string
        result_content = auto_moderator(file_path, content)
        if result_content:
            return """
            <script>
                alert("Content contains a curse word. Please enter different content.");
                window.location.href = '/post/createPost';  // Redirect back to the createPost page
            </script>
            """
        image_path = ''

        # Check if an image file is provided
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '' and allowed_file(image.filename):
                # Securely save the uploaded image

                filename = secure_filename(image.filename)
                image.save(os.path.join('uploads/', filename))
                image_path = os.path.join('../uploads/', filename)
        
        if exist_post(title):
            createPost_message = "Title has been used. "
            return """
            <script>
                alert("Title has been used.");
                window.location.href = '/post/createPost';  // Redirect back to the createPost page
            </script>
            """
        else:
            add_post(user_id, communityId, title, content, image_path)
            return redirect("/community/{}".format(communityId))
   
    username = session.get("username")
    communityName = session.get("location")

    if not username:
        return jsonify({'status': 'failed', 'message': 'Please log in firstly'}), 401

    return render_template('/createPost.html',communityName = communityName)

#Getting a specific posts from all posts
@post_blueprint.route('/community/<int:community_id>/posts', methods=['GET'])
def get_posts_by_community(community_id):
    user_check, user_data = check_session()
   
    if not user_check:
        return user_data
    username, communityName = user_data
   
    posts = get_postList_in_community(community_id)

    posts.reverse()

    return render_template('PostList.html',posts=posts,community_id=community_id)

#Curse word logic
def auto_moderator(file_path, search_string):
    try:
        with open(file_path, 'r') as file:
            bad_words = [word.strip().lower() for word in file.read().split(',')]
            pattern = re.compile(r'\b(?:' + '|'.join(re.escape(word) for word in bad_words) + r')\b', flags=re.IGNORECASE)
            if pattern.search(search_string):
                return True
        return False

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return False

@post_blueprint.route("/deletePost/<int:id>", methods=["POST"])
def deletePost(id):
    if request.method == 'POST':
        user_check, user_data = check_session()
        if not user_check:
            return user_data
        username, communityName = user_data
   
        post = delete_post_by_id(id)
        if post:
            return jsonify({'success': True, 'message': 'Post deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to delete post'})


# Single post route
@post_blueprint.route("/<int:id>", methods=["POST","GET"])
def show_post(id):
    user_check, user_data = check_session()
   
    if not user_check:
        return user_data
    username = user_data[0]
   
    post = get_post_by_id(id)
    communityList = get_communityList()[:]
    comments = get_comments_by_postId(id)
    userId = get_user_id_by_username(username)['id']
    ifLiked = if_liked(userId, id)

    if request.method == "POST":
        action = request.form.get('action')

        if action == 'comment':
            content = request.form.get('content')
            add_comment(content,id,username)

        if action == 'like':
            if ifLiked:
                likeId = get_like(userId,id)['id']
                delete_like(likeId)
                delete_likeNum(id)
            else:
                add_like(userId,id)
                add_likeNum(id)

        return redirect(url_for('post.show_post',id=id))

    comments.reverse()

    return render_template('singlePost.html', post=post, communityList=communityList,
                               comments=comments,ifLiked=ifLiked,postId=id)
   
@post_blueprint.route("/usersPosts", methods=["GET"])
def usersPosts():
    if request.method == 'GET':
        user_check, user_data = check_session()
   
        if not user_check:
            return user_data
        username, communityName = user_data
        id = session.get("user_id")

        post = get_usersPosts(id)

        post.reverse()

        return render_template('usersPosts.html', posts=post)


