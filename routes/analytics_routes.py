from flask import Blueprint, request, jsonify
from datetime import datetime
from analytics.sales_analytics import SalesAnalytics
from http import HTTPStatus

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/sales', methods=['GET'])
def get_sales_analytics():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        result = SalesAnalytics.get_sales_by_company(start_date, end_date)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': 'Formato data non valido'}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@analytics_bp.route('/analytics/inventory', methods=['GET'])
def get_inventory_analytics():
    try:
        result = SalesAnalytics.get_inventory_analysis()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@analytics_bp.route('/analytics/profit', methods=['GET'])
def get_profit_analytics():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        result = SalesAnalytics.get_profit_analysis(start_date, end_date)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': 'Formato data non valido'}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@analytics_bp.route('/analytics/sales/trend', methods=['GET'])
def get_sales_trend():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        result = SalesAnalytics.get_sales_trend(start_date, end_date)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': 'Formato data non valido'}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@analytics_bp.route('/analytics/items/top', methods=['GET'])
def get_top_items():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', default=10, type=int)
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        result = SalesAnalytics.get_top_items_analysis(start_date, end_date, limit)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': 'Formato data non valido'}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR 