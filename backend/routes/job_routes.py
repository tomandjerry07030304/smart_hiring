from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from bson import ObjectId
import numpy as np
from collections import Counter

from backend.models.database import get_db
from backend.models.job import Job, Application
from backend.utils.matching import extract_skills
from backend.services.fairness_engine import FairnessMetrics
from backend.services.fair_shortlisting import apply_fair_shortlisting

bp = Blueprint('jobs', __name__)

@bp.route('/create', methods=['POST'])
@jwt_required()
def create_job():
    """Create a new job posting (recruiter only)"""
    try:
        print("🎯 Job creation attempt")
        user_id = get_jwt_identity()  # This is now a string (user_id)
        claims = get_jwt()  # This contains additional claims like 'role'
        role = claims.get('role', 'candidate')
        
        print(f"👤 Current user ID: {user_id}, Role: {role}")
        
        # Check if user is recruiter/company/admin
        if role not in ['recruiter', 'company', 'admin']:
            print(f"❌ Access denied - role: {role}")
            return jsonify({'error': 'Only recruiters/companies can create job postings'}), 403
        
        data = request.get_json()
        print(f"📦 Received job data: {list(data.keys())}")
        
        # Validate required fields
        required_fields = ['title', 'description']
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing field: {field}")
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        print(f"✅ Validation passed - Title: {data['title'][:50]}...")
        
        # Extract skills from job description
        job_skills = data.get('required_skills', [])
        if not job_skills:
            job_skills = extract_skills(data['description'])
        
        print(f"🔧 Skills: {job_skills}")
        
        # Create job
        job = Job(
            title=data['title'],
            description=data['description'],
            recruiter_id=user_id,  # Use the user_id from JWT identity
            company_name=data.get('company_name', ''),
            location=data.get('location', ''),
            job_type=data.get('job_type', 'Full-time'),
            required_skills=job_skills,
            experience_required=data.get('experience_required', 0),
            salary_range=data.get('salary_range', {}),
            deadline=data.get('deadline', None)
        )
        
        print("💾 Inserting job into database...")
        db = get_db()
        jobs_collection = db['jobs']
        result = jobs_collection.insert_one(job.to_dict())
        
        print(f"✅ Job created with ID: {result.inserted_id}")
        return jsonify({
            'message': 'Job created successfully',
            'job_id': str(result.inserted_id),
            'required_skills': job_skills
        }), 201
        
    except Exception as e:
        print(f"❌ Job creation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/list', methods=['GET'])
def list_jobs():
    """Get list of all active job postings"""
    try:
        db = get_db()
        jobs_collection = db['jobs']
        
        # Get query parameters
        status = request.args.get('status', 'open')
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        # Query jobs
        query = {'status': status}
        jobs = list(jobs_collection.find(query).sort('posted_date', -1).skip(skip).limit(limit))
        
        # Convert ObjectId to string
        for job in jobs:
            job['_id'] = str(job['_id'])
            job['recruiter_id'] = str(job['recruiter_id'])
        
        return jsonify({
            'jobs': jobs,
            'count': len(jobs),
            'total': jobs_collection.count_documents(query)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/company', methods=['GET'])
@jwt_required()
def get_company_jobs():
    """Get jobs posted by the logged-in recruiter/company"""
    try:
        user_id = get_jwt_identity()
        print(f"📋 Fetching jobs for recruiter: {user_id}")
        
        db = get_db()
        jobs_collection = db['jobs']
        
        # Get query parameters
        status = request.args.get('status', 'open')
        
        # Query jobs for this recruiter
        query = {'recruiter_id': user_id}
        if status:
            query['status'] = status
            
        jobs = list(jobs_collection.find(query).sort('posted_date', -1))
        
        print(f"✅ Found {len(jobs)} jobs for recruiter {user_id}")
        
        # Convert ObjectId to string
        for job in jobs:
            job['_id'] = str(job['_id'])
            job['recruiter_id'] = str(job['recruiter_id'])
            # Convert datetime to ISO format string if present
            if 'posted_date' in job:
                job['posted_date'] = job['posted_date'].isoformat() if hasattr(job['posted_date'], 'isoformat') else str(job['posted_date'])
            if 'created_at' in job:
                job['created_at'] = job['created_at'].isoformat() if hasattr(job['created_at'], 'isoformat') else str(job['created_at'])
            if 'updated_at' in job:
                job['updated_at'] = job['updated_at'].isoformat() if hasattr(job['updated_at'], 'isoformat') else str(job['updated_at'])
        
        return jsonify({
            'jobs': jobs,
            'count': len(jobs)
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching company jobs: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/company/stats', methods=['GET'])
@jwt_required()
def get_company_stats():
    """Get dashboard statistics for the logged-in recruiter/company"""
    try:
        user_id = get_jwt_identity()
        print(f"📊 Fetching stats for recruiter: {user_id}")
        
        db = get_db()
        jobs_collection = db['jobs']
        applications_collection = db['applications']
        
        # Count active jobs
        active_jobs = jobs_collection.count_documents({
            'recruiter_id': user_id,
            'status': 'open'
        })
        
        # Get all job IDs for this recruiter
        recruiter_jobs = list(jobs_collection.find(
            {'recruiter_id': user_id},
            {'_id': 1}
        ))
        job_ids = [str(job['_id']) for job in recruiter_jobs]
        
        # Count total applications
        total_applications = applications_collection.count_documents({
            'job_id': {'$in': job_ids}
        }) if job_ids else 0
        
        # Count applications by status
        applications_by_status = {}
        if job_ids:
            pipeline = [
                {'$match': {'job_id': {'$in': job_ids}}},
                {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
            ]
            for doc in applications_collection.aggregate(pipeline):
                applications_by_status[doc['_id']] = doc['count']
        
        print(f"✅ Stats: {active_jobs} jobs, {total_applications} applications")
        
        return jsonify({
            'active_jobs': active_jobs,
            'total_jobs': len(recruiter_jobs),
            'total_applications': total_applications,
            'shortlisted': applications_by_status.get('shortlisted', 0),
            'interviewed': applications_by_status.get('screening', 0),
            'hired': applications_by_status.get('hired', 0)
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/company/applications', methods=['GET'])
@jwt_required()
def get_company_applications():
    """Get all applications for jobs posted by the logged-in recruiter"""
    try:
        user_id = get_jwt_identity()
        
        db = get_db()
        jobs_collection = db['jobs']
        applications_collection = db['applications']
        users_collection = db['users']
        
        # Get all job IDs for this recruiter
        recruiter_jobs = list(jobs_collection.find(
            {'recruiter_id': user_id},
            {'_id': 1, 'title': 1, 'company_name': 1}
        ))
        
        if not recruiter_jobs:
            return jsonify({'applications': [], 'count': 0}), 200
            
        # Create a map of job_id to job info for enrichment
        job_map = {str(job['_id']): {'title': job['title'], 'company_name': job.get('company_name', '')} for job in recruiter_jobs}
        job_ids = list(job_map.keys())
        
        # Get applications for these jobs
        applications = list(applications_collection.find(
            {'job_id': {'$in': job_ids}}
        ).sort('applied_date', -1))
        
        # Enrich applications with job and candidate information
        for app in applications:
            app['_id'] = str(app['_id'])
            job_info = job_map.get(app['job_id'], {})
            app['job_title'] = job_info.get('title', 'Unknown Job')
            app['company_name'] = job_info.get('company_name', '')
            
            # Get candidate information
            candidate_id = app.get('candidate_id')
            if candidate_id:
                candidate_user = users_collection.find_one({'_id': ObjectId(candidate_id)})
                if candidate_user:
                    app['candidate_name'] = candidate_user.get('full_name', 'Unknown')
                    app['candidate_email'] = candidate_user.get('email', '')
                else:
                    app['candidate_name'] = 'Unknown'
                    app['candidate_email'] = ''
            else:
                app['candidate_name'] = 'Unknown'
                app['candidate_email'] = ''
            
            # Ensure dates are properly formatted
            if 'applied_date' in app:
                app['applied_at'] = app['applied_date'].isoformat() if hasattr(app['applied_date'], 'isoformat') else str(app['applied_date'])
            elif 'applied_at' in app:
                app['applied_at'] = app['applied_at'].isoformat() if hasattr(app['applied_at'], 'isoformat') else str(app['applied_at'])
            else:
                app['applied_at'] = datetime.utcnow().isoformat()
            
            # Ensure score fields exist
            if 'overall_score' not in app:
                app['overall_score'] = 0
        
        return jsonify({
            'applications': applications,
            'count': len(applications)
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching company applications: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get job details by ID"""
    try:
        db = get_db()
        jobs_collection = db['jobs']
        
        job = jobs_collection.find_one({'_id': ObjectId(job_id)})
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        job['_id'] = str(job['_id'])
        job['recruiter_id'] = str(job['recruiter_id'])
        
        return jsonify(job), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    """Update job posting (recruiter only, own jobs)"""
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] not in ['recruiter', 'admin']:
            return jsonify({'error': 'Only recruiters can update jobs'}), 403
        
        db = get_db()
        jobs_collection = db['jobs']
        
        # Check if job exists and user owns it
        job = jobs_collection.find_one({'_id': ObjectId(job_id)})
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if str(job['recruiter_id']) != current_user['user_id'] and current_user['role'] != 'admin':
            return jsonify({'error': 'Not authorized to update this job'}), 403
        
        data = request.get_json()
        
        # Fields that can be updated
        allowed_fields = ['title', 'description', 'company_name', 'location', 'job_type', 
                         'required_skills', 'experience_required', 'salary_range', 'status', 'deadline']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        update_data['updated_at'] = datetime.utcnow()
        
        result = jobs_collection.update_one(
            {'_id': ObjectId(job_id)},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            return jsonify({'message': 'Job updated successfully'}), 200
        else:
            return jsonify({'message': 'No changes made'}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<job_id>/applications', methods=['GET'])
@jwt_required()
def get_job_applications(job_id):
    """Get all applications for a job (recruiter only)"""
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] not in ['recruiter', 'admin']:
            return jsonify({'error': 'Only recruiters can view applications'}), 403
        
        db = get_db()
        jobs_collection = db['jobs']
        applications_collection = db['applications']
        
        # Verify job ownership
        job = jobs_collection.find_one({'_id': ObjectId(job_id)})
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if str(job['recruiter_id']) != current_user['user_id'] and current_user['role'] != 'admin':
            return jsonify({'error': 'Not authorized'}), 403
        
        # Get applications
        applications = list(applications_collection.find({'job_id': job_id}).sort('overall_score', -1))
        
        # Convert ObjectId to string
        for app in applications:
            app['_id'] = str(app['_id'])
        
        return jsonify({
            'job_id': job_id,
            'applications': applications,
            'count': len(applications)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<job_id>/fairness-report', methods=['GET'])
@jwt_required()
def get_fairness_report(job_id):
    """
    Generate comprehensive fairness audit report for a job
    
    Analyzes hiring decisions for bias using multiple fairness metrics:
    - Demographic Parity (selection rate equality)
    - Disparate Impact (80% rule compliance)
    - Equal Opportunity (TPR equality)
    
    Returns actionable recommendations if bias detected.
    """
    try:
        current_user = get_jwt_identity()
        
        # Only recruiters and admins can view fairness reports
        if current_user['role'] not in ['recruiter', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        
        db = get_db()
        jobs_collection = db['jobs']
        applications_collection = db['applications']
        candidates_collection = db['candidates']
        
        # Verify job exists and user has access
        job = jobs_collection.find_one({'_id': ObjectId(job_id)})
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if str(job['recruiter_id']) != current_user['user_id'] and current_user['role'] != 'admin':
            return jsonify({'error': 'Not authorized to view this report'}), 403
        
        # Get all applications for this job
        applications = list(applications_collection.find({'job_id': job_id}))
        
        if len(applications) < 10:
            return jsonify({
                'warning': 'Insufficient data for fairness analysis',
                'message': 'Need at least 10 applications for meaningful statistical analysis',
                'total_applicants': len(applications),
                'job_id': job_id
            }), 200
        
        # Extract hiring decisions and demographics
        predictions = []
        labels = []
        sensitive_features = []
        demographics_breakdown = {'total': len(applications), 'by_status': {}, 'by_group': {}}
        
        for app in applications:
            # Prediction: 1 if shortlisted, 0 otherwise
            status = app.get('status', 'submitted')
            pred = 1 if status in ['shortlisted', 'interviewed', 'hired'] else 0
            predictions.append(pred)
            
            # For now, we don't have ground truth, so use predictions as proxy
            labels.append(pred)
            
            # Get demographic data (if available - optional survey)
            # Note: Collecting demographic data is OPTIONAL and only for fairness auditing
            candidate = candidates_collection.find_one({'user_id': app.get('user_id')})
            
            # Try to infer gender from optional demographic field (NOT from resume)
            gender = 'unknown'
            if candidate:
                # Check if user voluntarily provided demographic info
                gender = candidate.get('demographic_gender', 'unknown')
                
                # Fallback: check if gender field exists (from old data)
                if gender == 'unknown':
                    gender = candidate.get('gender', 'unknown')
            
            sensitive_features.append(gender)
            
            # Count by status
            demographics_breakdown['by_status'][status] = demographics_breakdown['by_status'].get(status, 0) + 1
        
        # Count demographics
        demographics_breakdown['by_group'] = dict(Counter(sensitive_features))
        
        # Remove 'unknown' from fairness calculation if we have known groups
        known_groups = [g for g in sensitive_features if g != 'unknown']
        known_predictions = [p for p, g in zip(predictions, sensitive_features) if g != 'unknown']
        known_labels = [l for l, g in zip(labels, sensitive_features) if g != 'unknown']
        
        # Check if we have enough known demographic data
        if len(set(known_groups)) < 2 or len(known_groups) < 5:
            return jsonify({
                'status': 'incomplete_data',
                'message': 'Insufficient demographic data for fairness analysis',
                'explanation': 'Demographic information is collected voluntarily and anonymously for fairness auditing only. Not enough applicants have provided this information.',
                'total_applicants': len(applications),
                'with_demographic_data': len(known_groups),
                'demographics': demographics_breakdown,
                'job_id': job_id
            }), 200
        
        # Calculate fairness metrics
        try:
            fm = FairnessMetrics(
                predictions=np.array(known_predictions),
                labels=np.array(known_labels),
                sensitive_features=np.array(known_groups),
                favorable_label=1
            )
            
            # Get key metrics
            dem_parity_diff = fm.demographic_parity_difference()
            dem_parity_ratio = fm.demographic_parity_ratio()
            disparate_impact = fm.disparate_impact()
            equal_opp_diff = fm.equal_opportunity_difference()
            
            # Calculate selection rates per group
            group_stats = {}
            for group in set(known_groups):
                group_mask = [g == group for g in known_groups]
                group_total = sum(group_mask)
                group_selected = sum([p for p, mask in zip(known_predictions, group_mask) if mask])
                
                group_stats[group] = {
                    'total_applicants': group_total,
                    'shortlisted': group_selected,
                    'selection_rate': group_selected / group_total if group_total > 0 else 0
                }
            
            # Check 80% rule compliance
            di_ratios = list(disparate_impact.values())
            passes_80_rule = all(ratio >= 0.8 for ratio in di_ratios)
            
            # Generate recommendations
            recommendations = []
            severity_level = 'LOW'
            
            # Check for demographic parity violation
            if abs(dem_parity_diff) > 0.1:
                severity_level = 'HIGH'
                recommendations.append({
                    'severity': 'HIGH',
                    'metric': 'Demographic Parity',
                    'issue': f'Selection rates differ by {abs(dem_parity_diff):.1%} across groups',
                    'threshold': '10% difference',
                    'action': 'Review shortlisting criteria and scoring weights. Consider using fairness-aware ranking algorithm.',
                    'legal_note': 'May indicate adverse impact under EEOC guidelines'
                })
            
            # Check for 80% rule violation
            if not passes_80_rule:
                severity_level = 'CRITICAL'
                min_ratio = min(di_ratios)
                recommendations.append({
                    'severity': 'CRITICAL',
                    'metric': 'Disparate Impact (80% Rule)',
                    'issue': f'Fails 80% rule with ratio of {min_ratio:.2%}',
                    'threshold': '80% minimum',
                    'action': 'IMMEDIATE ACTION REQUIRED: Adjust selection thresholds or implement fairness constraints. This may violate legal requirements.',
                    'legal_note': 'Violates EEOC Uniform Guidelines on Employee Selection Procedures'
                })
            
            # Check for equal opportunity violation
            if abs(equal_opp_diff) > 0.1:
                if severity_level not in ['CRITICAL', 'HIGH']:
                    severity_level = 'MEDIUM'
                recommendations.append({
                    'severity': 'MEDIUM',
                    'metric': 'Equal Opportunity',
                    'issue': f'Qualified candidates have unequal selection rates across groups ({abs(equal_opp_diff):.1%} difference)',
                    'threshold': '10% difference in TPR',
                    'action': 'Review assessment scoring to ensure equal treatment of qualified candidates from all groups'
                })
            
            # If no issues, provide positive feedback
            if not recommendations:
                severity_level = 'PASS'
                recommendations.append({
                    'severity': 'PASS',
                    'metric': 'All Fairness Metrics',
                    'issue': 'No fairness violations detected',
                    'action': 'Continue current hiring practices. Monitor ongoing.'
                })
            
            fairness_report = {
                'job_id': job_id,
                'job_title': job.get('title', 'Unknown'),
                'analysis_date': datetime.utcnow().isoformat(),
                'total_applicants': len(applications),
                'analyzed_applicants': len(known_groups),
                'demographics': demographics_breakdown,
                'group_statistics': group_stats,
                'fairness_metrics': {
                    'demographic_parity_difference': {
                        'value': float(dem_parity_diff),
                        'interpretation': 'Difference in selection rates between groups',
                        'threshold': 0.1,
                        'passes': abs(dem_parity_diff) <= 0.1
                    },
                    'demographic_parity_ratio': {
                        'value': float(dem_parity_ratio),
                        'interpretation': 'Ratio of selection rates',
                        'threshold': 0.8,
                        'passes': dem_parity_ratio >= 0.8
                    },
                    'disparate_impact': {
                        'values': {k: float(v) for k, v in disparate_impact.items()},
                        'interpretation': 'Pairwise selection rate ratios (80% rule)',
                        'threshold': 0.8,
                        'passes': passes_80_rule
                    },
                    'equal_opportunity_difference': {
                        'value': float(equal_opp_diff),
                        'interpretation': 'Difference in true positive rates',
                        'threshold': 0.1,
                        'passes': abs(equal_opp_diff) <= 0.1
                    }
                },
                'compliance': {
                    'passes_80_percent_rule': passes_80_rule,
                    'passes_demographic_parity': abs(dem_parity_diff) <= 0.1,
                    'passes_equal_opportunity': abs(equal_opp_diff) <= 0.1,
                    'overall_severity': severity_level
                },
                'recommendations': recommendations,
                'legal_disclaimer': 'This report is for internal fairness auditing only and does not constitute legal advice. Consult with legal counsel for compliance guidance.'
            }
            
            # Log this audit
            db['fairness_audits'].insert_one({
                'job_id': job_id,
                'recruiter_id': str(job['recruiter_id']),
                'report': fairness_report,
                'timestamp': datetime.utcnow()
            })
            
            return jsonify(fairness_report), 200
            
        except Exception as fairness_error:
            return jsonify({
                'error': 'Failed to calculate fairness metrics',
                'details': str(fairness_error),
                'total_applicants': len(applications)
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<job_id>/fair-shortlist', methods=['POST'])
@jwt_required()
def fair_shortlist_candidates(job_id):
    """
    Apply fairness-aware shortlisting to job applicants
    
    Uses fairness algorithms to ensure unbiased candidate selection:
    - Post-processing: Adjusts shortlist after scoring (80% rule)
    - Re-weighting: Adjusts scores based on group representation
    - Threshold optimization: Per-group score thresholds
    
    Request body:
    {
        "method": "postprocessing" | "reweighting" | "threshold_optimization",
        "selection_percentage": 0.2,  // 20% of applicants
        "protected_attribute": "gender",  // demographic attribute to check
        "threshold": 0.8  // disparate impact threshold (80% rule)
    }
    """
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] not in ['recruiter', 'admin']:
            return jsonify({'error': 'Only recruiters can shortlist candidates'}), 403
        
        db = get_db()
        jobs_collection = db['jobs']
        applications_collection = db['applications']
        candidates_collection = db['candidates']
        
        # Verify job ownership
        job = jobs_collection.find_one({'_id': ObjectId(job_id)})
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if str(job['recruiter_id']) != current_user['user_id'] and current_user['role'] != 'admin':
            return jsonify({'error': 'Not authorized'}), 403
        
        # Get parameters
        data = request.get_json() or {}
        method = data.get('method', 'postprocessing')
        selection_percentage = data.get('selection_percentage', 0.2)
        protected_attribute = data.get('protected_attribute', 'gender')
        threshold = data.get('threshold', 0.8)
        
        # Get all applications with scores
        applications = list(applications_collection.find({'job_id': job_id}))
        
        if len(applications) < 5:
            return jsonify({
                'error': 'Too few applications',
                'message': 'Need at least 5 applications for fair shortlisting',
                'total': len(applications)
            }), 400
        
        # Enrich applications with candidate data
        enriched_candidates = []
        for app in applications:
            candidate = candidates_collection.find_one({'user_id': app.get('user_id')})
            
            if candidate:
                # Combine application and candidate data
                enriched = {
                    'application_id': str(app['_id']),
                    'user_id': app.get('user_id'),
                    'overall_score': app.get('overall_score', 0),
                    'skill_match_score': app.get('skill_match_score', 0),
                    'resume_match_score': app.get('resume_match_score', 0),
                    'cci_score': app.get('cci_score'),
                    protected_attribute: candidate.get(f'demographic_{protected_attribute}', 
                                                      candidate.get(protected_attribute, 'unknown'))
                }
                enriched_candidates.append(enriched)
        
        if not enriched_candidates:
            return jsonify({'error': 'No valid candidates found'}), 400
        
        # Apply fair shortlisting algorithm
        try:
            shortlisted, fairness_report = apply_fair_shortlisting(
                candidates=enriched_candidates,
                method=method,
                protected_attribute=protected_attribute,
                selection_percentage=selection_percentage,
                threshold=threshold
            )
            
            # Update application statuses
            shortlisted_ids = [c['application_id'] for c in shortlisted]
            
            # Mark as shortlisted
            applications_collection.update_many(
                {'_id': {'$in': [ObjectId(sid) for sid in shortlisted_ids]}},
                {'$set': {
                    'status': 'shortlisted',
                    'shortlisted_date': datetime.utcnow(),
                    'shortlisting_method': method,
                    'fairness_adjusted': fairness_report.get('adjustment_made', False)
                }}
            )
            
            # Mark others as screened (not shortlisted)
            not_shortlisted = [
                ObjectId(c['application_id']) for c in enriched_candidates 
                if c['application_id'] not in shortlisted_ids
            ]
            applications_collection.update_many(
                {'_id': {'$in': not_shortlisted}},
                {'$set': {
                    'status': 'screened',
                    'screened_date': datetime.utcnow()
                }}
            )
            
            # Log fairness audit
            db['fairness_audits'].insert_one({
                'job_id': job_id,
                'recruiter_id': str(job['recruiter_id']),
                'action': 'fair_shortlisting',
                'method': method,
                'report': fairness_report,
                'shortlisted_count': len(shortlisted),
                'total_applicants': len(enriched_candidates),
                'timestamp': datetime.utcnow()
            })
            
            return jsonify({
                'message': 'Fair shortlisting completed',
                'method': method,
                'total_applicants': len(enriched_candidates),
                'shortlisted': len(shortlisted),
                'fairness_report': fairness_report,
                'shortlisted_ids': shortlisted_ids
            }), 200
            
        except Exception as fairness_error:
            return jsonify({
                'error': 'Fair shortlisting failed',
                'details': str(fairness_error)
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
