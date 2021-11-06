import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add(
      "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
      )
    response.headers.add(
      "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
      )
    return response
  
    '''
  @temp: 
  Create temp route to avoid 404 error.
  '''
  @app.route("/")
  def test():
    return jsonify({
        'success': True
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route("/categories", methods=["GET"])
  def retrieve_categories():
    selection = Category.query.order_by(Category.id).all()
    categories = {category.id:category.type for category in selection}

    return jsonify(
        {
          "success":True,
          "categories": categories
        }
    )

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    page_questions = questions[start:end]
    total_question = len(questions)

    return page_questions, total_question

  
  @app.route('/questions', methods=["GET"])
  def retrieve_questions_per_page():
    all_questions = Question.query.order_by(Question.id).all()
    page_questions, total_question = paginate_questions(request, all_questions)

    if len(page_questions) == 0:
      abort(404)

    all_categories = Category.query.order_by(Category.id).all()
    categories = {category.id:category.type for category in all_categories}
    
    return jsonify({
        'questions': page_questions,
        'totalQuestions': total_question,
        'categories': categories,
        'currentCategory': None
    })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:q_id>', methods=["DELETE"])
  def delete_question(q_id):
    question = Question.query.filter(Question.id == q_id).one_or_none()

    if question:
      Question.delete(question)
      return jsonify({
        "success": True
      })

    abort(404)



  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions', methods=["POST"])
  def create_search_question():
    body = request.get_json()

    question = body.get("question", None)
    answer = body.get("answer", None)
    difficulty = body.get("difficulty", None)
    category = body.get("category", None)
    search_term = body.get('searchTerm', None)

    if search_term is None:
      try:
        question = Question(question = question,answer = answer, difficulty = difficulty, category = category)
        question.insert()

        return jsonify(
          {
            "success": True
          }
        )

      except:
        abort(422)

    else:
      search_questions = Question.query.filter(Question.question.ilike('%{}%'.format(search_term)))
      page_questions, total_question = paginate_questions(request, search_questions)

      if len(page_questions) == 0:
        abort(404)

      return jsonify({
          'questions': page_questions,
          'totalQuestions': total_question,
          'currentCategory': None
      })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions', methods=["GET"])
  def retrieve_question_in_category(category_id):
    cat_questions = Question.query.filter(Question.category == category_id).all()

    page_questions, total_question = paginate_questions(request, cat_questions)

    if total_question==0:
      abort(404)
    
    category = Category.query.filter(Category.id == category_id).one_or_none()

    if category is None:
      abort(404)

    category_name = category.type

    return jsonify({
      'success':True,
      'questions': page_questions,
      'totalQuestions': total_question,
      'currentCategory': category_name
      }) 

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=["POST"])
  def show_quizzes():
    body = request.get_json()
    previous_id_list = body.get("previous_questions", None)
    category_id = int(body['quiz_category']['id'])

    if category_id == 0:
      cat_questions = Question.query.all()
    else:
      cat_questions = Question.query.filter(Question.category == category_id).all()

    cat_id_list = [question.id for question in cat_questions]

    for val in previous_id_list:
      if val in cat_id_list:
        cat_id_list.remove(val)        
    
    # if the category only has one question,
    # show previous question repeatedly.
    if len(cat_id_list) == 0:
      cat_id_list = previous_id_list
    
    next_id = random.choice(cat_id_list)
    next_question = Question.query.get(next_id)

    next_question = next_question.format()


    return jsonify({
      'success':True,
      'question': next_question
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  
  @app.errorhandler(404)
  def not_found(error):
    return (
      jsonify({"success": False, "error": 404, "message": "resource not found"}),
      404,
    )

  @app.errorhandler(422)
  def unprocessable(error):
    return (
      jsonify({"success": False, "error": 422, "message": "unprocessable"}),
      422,
      )

    
  @app.errorhandler(400)
  def bad_request(error):
    return (
      jsonify({"success": False, "error": 400, "message": "bad request"}),
      400,
      )

  @app.errorhandler(405)
  def not_found(error):
    return (
      jsonify({"success": False, "error": 405, "message": "method not allowed"}),
      405,
      )

  @app.errorhandler(500)
  def not_found(error):
    return (
      jsonify({"success": False, "error": 500, "message": "Internal Server Error"}),
      500,
      )

  
  return app

    