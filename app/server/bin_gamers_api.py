from flask import Blueprint
from flask_restful import Api, Resource
from server import models, cache, db
from sqlalchemy_searchable import search
import subprocess
api = Api(Blueprint('api', __name__)) # pylint: disable=invalid-name


@api.resource('/companies')
class CompaniesAPI(Resource):
    @staticmethod
    @cache.cached()
    def get():
        Company = models.Company
        q = Company.query.all()
        return companyListFormat(q)

@api.resource('/companies/<int:company_id>')
class CompanyAPI(Resource):
    @staticmethod
    @cache.cached()
    def get(company_id):
        Company = models.Company
        c = Company.query.filter_by(company_id = company_id).first()
        if not c:
            return []
        return companyFormat(c)

@api.resource('/games')
class GamesAPI(Resource):
    @staticmethod
    @cache.cached()
    def get():
        Game = models.Game
        q = Game.query.all()
        return gameListFormat(q)

@api.resource('/games/<int:game_id>')
class GameAPI(Resource):
    @staticmethod
    @cache.cached()
    def get(game_id):
        Game = models.Game
        g = Game.query.filter_by(game_id = game_id).first()
        if not g:
            return []
        return gameFormat(g)

@api.resource('/years')
class YearsAPI(Resource):
    @staticmethod
    @cache.cached()
    def get():
        Year = models.Year
        q = Year.query.all()
        return yearListFormat(q)

@api.resource('/years/<int:year_id>')
class YearAPI(Resource):
    @staticmethod
    @cache.cached()
    def get(year_id):
        Year = models.Year
        y = Year.query.filter_by(year_id = year_id).first()
        if not y:
            return []
        else:
            return yearFormat(y)


@api.resource('/search/<string:search_term>')
class SearchAPI(Resource):
    @staticmethod
    def get(search_term):
        # Check if the search term has a space in it. If so, need to do an OR query
        if ' ' in search_term:
            return {
                'and' : and_query(search_term),
                'or'  : or_query(search_term)
            }
        else:
            return {
                'and' : and_query(search_term),
                'or'  : []
            }


def or_query(query_term):
    terms_list = query_term.strip().split(' ')
    splitter = " or "
    query_term = splitter.join(terms_list)
    return and_query(query_term)


def and_query(query_term):
    Company = models.Company
    Game = models.Game
    Year = models.Year
    c = Company.query.search(query_term).all()
    g = Game.query.search(query_term).all()
    y = Year.query.search(query_term).all()
    print(c)
    print(g)
    print(y)
    if not c and not g and not y:
        return []
    return [{
        "companies" : companyListFormat(c),
        "games"     : gameListFormat(g),
        "years"     : yearListFormat(y)
    }]




@api.resource('/tests')
class TestOutput(Resource):
    @staticmethod
    def get():
        proc = subprocess.Popen(["python3", "tests.py"], stdout=subprocess.PIPE,
                                stderr= subprocess.STDOUT, universal_newlines=True)
        output = proc.stdout.read()
        return output








def companyFormat(c):
    return [{
        "company_id" : c.company_id,
        "name" : c.name,
        "num_developed" :  c.num_developed,
        "num_published" : c.num_published,
        "avg_rating" : float("%.2f" % c.avg_rating) if c.avg_rating else None,
        "year" : c.year_founded,
        "games_to_url" : [{ "name": i.name, "url" : ("/games/" + str(i.game_id))} for i in c.associated_games],
        "image_url" : c.image_url
    }]

def companyListFormat(q):
    return [ {
        "company_id" : c.company_id,
        " Company" : c.name,
        "Number of Games Developed" :  c.num_developed,
        "Number of Games Published" : c.num_published,
        "Average Rating" : float("%.2f" % c.avg_rating) if c.avg_rating else None,
        "Year Founded" : c.year_founded,
        } for c in q]

def gameFormat(g):
    return [{
        "game_id" : g.game_id,
        "name" : g.name,
        "genres" : [i.genre_name for i in g.associated_genres],
        "platforms" : [i.platform_name for i in g.associated_platforms],
        "companies_to_url" : [{"name" : i.name, "url" : ("/companies/" + str(i.company_id))} for i in g.associated_companies],
        "rating" : float("%.2f" % g.rating) if g.rating else None,
        "year" : g.release_year,
        "image_url" : g.image_url
    }]

def gameListFormat(q):
    return [{
                "game_id" : g.game_id,
                " Game" : g.name,
                "Genres" : [i.genre_name for i in g.associated_genres],
                "Platforms" : [i.platform_name for i in g.associated_platforms],
                "Companies" : [i.name for i in g.associated_companies],
                "Rating" : float("%.2f" % g.rating) if g.rating else None,
                "Year" : g.release_year
            } for g in q]

def yearListFormat(q):
    return [{
                " Year" : y.year_id,
                "Number of Games" : len(y.games),
                "Most Popular Genre" : y.most_popular_genre,
                "Average Rating" : float("%.2f" % y.avg_rating) if y.avg_rating else None,
                "Number of Companies Founded" : len(y.companies_founded)
            } for y in q]

def yearFormat(y):
    return [{
        "year_id" : y.year_id,
        "num_games" : y.num_games,
        "most_popular_genre" : y.most_popular_genre,
        "avg_rating" : float("%.2f" % y.avg_rating) if y.avg_rating else None,
        "companies_to_url" : [{"name" : i.name, "url" : ("/companies/" + str(i.company_id))} for i in y.companies_founded],
        "games_to_url" : [{"name" : i.name, "url" : ("/games/" + str(i.game_id))} for i in y.games]
    }]
