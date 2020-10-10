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
        DB_USERNAME = "postgres"
        DB_PASSWORD = "postgres123"
        self.database_path = "postgresql://{}:{}@{}/{}".format(DB_USERNAME, DB_PASSWORD,'localhost:5432', self.database_name)
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
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
    
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], None)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_404_sent_reguesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=10000', json = {"category": 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')  

    # test delete question
    def test_delete_question(self):
        res = self.client().delete('/questions/49')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id ==49 ).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], None)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(question, None)
    # if question doesn't exist
    def test_404_if_question_does_not_exist(self):
        res = self.client().delete('/question/10000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found') 
    # if  question can't be delete 
    def test_422_if_question_delete_fail(self):
        res = self.client().delete('question/')
        data = json.loads(res.data) 
        # self.assertEqual(res.status_code, 422)
        # self.assertEqual(data['success'], False)
        # self.assertEqual(data['message'], 'unprocessable') 
        pass

    def test_create_question(self):
        new_question = {
            'question': 'How many time zones are there in Russia?',
            'answer': '11',
            'category': '3',
            'difficulty': 3}

        res = self.client().post('/questions/add', json = new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
    
    
    def test_404_if_question_creation_fails(self):
        new_question = {
            'question': 56,
            'answer': '11',
            'category': 3,
            'difficulty': 3}
        res = self.client().post('/question/add', json= new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found') 

     def test_422_if_question_creation_empty_data(self):
        new_question = {
            'question': '',
            'answer': '11',
            'category': 3,
            'difficulty': 3}
        res = self.client().post('/question/add', json= new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')     
    
    def test_searching_questions(self):
        res = self.client().get('/questions', json = {'searchTerm': 'why'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], None)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])  

    def test_searching_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], None)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])    
    
    
    def test_404_searching_questions_by_category_which_not_exist(self):
        res = self.client().get('/categories/20/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')  


    def test_play_game(self):
        res = self.client().post("/quizzes", json = {'previous_questions': [], 'quiz_category': {'type': 'Geography','id': '3'}}) 
    
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True) 
        self.assertEqual(len(data['question']), 5) 

    def test_422_if_get_question_for_game_fails(self):
        res = self.client().post("/quizzes", json = {'previous_questions': 0, 'quiz_category': {'id': '0', 'type': 'all'}}) 
        data = json.loads(res.data) 

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')      

if __name__ == "__main__":
    unittest.main()