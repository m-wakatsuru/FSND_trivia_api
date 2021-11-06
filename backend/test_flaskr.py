import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'postgres://postgres:s5V5wBxPyy@{}/{}'.format('localhost:5432', self.database_name)
        #self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_paginated_questions(self):
        res = self.client().get("/questions?page=1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data["questions"]), 10)
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["categories"]))

    def test_404_sent_get_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=100")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)        
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_delete_questions(self):
        res = self.client().delete("/questions/19")
        data = json.loads(res.data)

        self.assertEqual(data["success"], True)
    
    def test_404_sent_delete_requesting_beyond_valid_page(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)        
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    def test_creating_questions(self):
        test ={
            'question':  'Heres a new question string',
            'answer':  'Heres a new answer string',
            'difficulty': 1,
            'category': 3,
            }
        res = self.client().post("/questions", json =test)
        data = json.loads(res.data)

        self.assertEqual(data["success"],True)
    
    def test_422_creating_invalid_questions(self):
        test ={
            'question':  'Heres a new question string',
            'answer':  'Heres a new answer string',
            'difficulty': 'one',
            'category': 'three',
            }
        res = self.client().post("/questions", json =test)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)


    def test_searching_questions(self):
        res = self.client().post("/questions", json ={'searchTerm': 'title'})
        data = json.loads(res.data)

        self.assertTrue(data["questions"])
        self.assertTrue(data["totalQuestions"])
    
    def test_404_invalid_searching_questions(self):
        res = self.client().post("/questions", json ={'searchTerm': 'aaaaaaaa'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)        
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    def test_showing_specified_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(data["success"], True)

    def test_404_showing_invalid_specified_category(self):
        res = self.client().get("/questions/20/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_showing_next_quiz(self):
        test = {
            "previous_questions": [1, 4, 20, 15],
	        "quiz_category": "Science"
        }
        res = self.client().post("/quizzes", json = test)
        data = json.loads(res.data)

        self.assertEqual(data["success"], True)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()