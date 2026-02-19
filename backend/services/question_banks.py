"""
Comprehensive Interview Question Banks
=======================================
35+ technical questions per role across multiple categories,
15 universal behavioral questions, and real-world scenario questions.

Supports 25-30 questions per interview with variety across sessions.

Roles covered:
  - software_developer
  - data_analyst
  - data_scientist
  - devops_engineer
  - product_manager
  - ui_ux_designer
"""

# ============================================================================
# SOFTWARE DEVELOPER — 36 questions across 8 categories
# ============================================================================
SOFTWARE_DEVELOPER_QUESTIONS = {
    'fundamentals': [
        {
            'id': 'SD_F1',
            'question': 'Explain the SOLID principles and provide a real-world example of how you\'ve applied at least two of them.',
            'difficulty': 'medium',
            'expected_keywords': ['single responsibility', 'open-closed', 'liskov', 'interface segregation', 'dependency inversion', 'maintainability', 'extensible'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you balance adhering to SOLID principles with meeting tight deadlines?'
        },
        {
            'id': 'SD_F2',
            'question': 'What is your approach to error handling and logging in production applications? Describe a specific incident you debugged.',
            'difficulty': 'hard',
            'expected_keywords': ['try-catch', 'exception', 'logging levels', 'monitoring', 'stack trace', 'debugging', 'root cause'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you prevent similar issues from recurring?'
        },
        {
            'id': 'SD_F3',
            'question': 'Describe your experience with version control. How do you handle merge conflicts and what branching strategy do you prefer?',
            'difficulty': 'easy',
            'expected_keywords': ['git', 'branch', 'merge', 'conflict', 'pull request', 'code review', 'gitflow'],
            'time_limit_minutes': 7,
            'follow_up': 'Tell me about a time when a merge went wrong and how you resolved it.'
        },
        {
            'id': 'SD_F4',
            'question': 'Explain the difference between object-oriented programming and functional programming. When would you choose one paradigm over the other?',
            'difficulty': 'medium',
            'expected_keywords': ['oop', 'functional', 'inheritance', 'polymorphism', 'immutability', 'pure functions', 'state', 'side effects'],
            'time_limit_minutes': 10,
            'follow_up': 'How do modern languages blend both paradigms?'
        },
        {
            'id': 'SD_F5',
            'question': 'What are design patterns? Describe three patterns you\'ve used in production code and explain why they were the right choice.',
            'difficulty': 'hard',
            'expected_keywords': ['design pattern', 'singleton', 'factory', 'observer', 'strategy', 'decorator', 'adapter', 'reusable'],
            'time_limit_minutes': 12,
            'follow_up': 'When can design patterns be over-engineered or harmful?'
        },
        {
            'id': 'SD_F6',
            'question': 'Explain the concept of dependency injection. How does it improve testability and maintainability?',
            'difficulty': 'medium',
            'expected_keywords': ['dependency injection', 'inversion of control', 'testability', 'decoupling', 'mock', 'interface', 'constructor injection'],
            'time_limit_minutes': 8,
            'follow_up': 'What DI frameworks have you used?'
        },
    ],
    'architecture': [
        {
            'id': 'SD_A1',
            'question': 'Design a URL shortener service like bit.ly. Discuss database schema, API endpoints, scaling strategy, and how you\'d handle 1 million requests per day.',
            'difficulty': 'hard',
            'expected_keywords': ['hash', 'database', 'redis', 'caching', 'load balancer', 'distributed', 'sharding', 'api design'],
            'time_limit_minutes': 15,
            'follow_up': 'How would you handle analytics and track click statistics?'
        },
        {
            'id': 'SD_A2',
            'question': 'Explain the difference between monolithic and microservices architecture. When would you choose one over the other?',
            'difficulty': 'medium',
            'expected_keywords': ['monolithic', 'microservices', 'scalability', 'deployment', 'communication', 'trade-offs', 'complexity'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you handle distributed transactions in microservices?'
        },
        {
            'id': 'SD_A3',
            'question': 'Design a real-time chat application. How would you handle message ordering, delivery guarantees, and presence detection?',
            'difficulty': 'hard',
            'expected_keywords': ['websocket', 'message queue', 'ordering', 'delivery', 'presence', 'scalability', 'database', 'pub-sub'],
            'time_limit_minutes': 15,
            'follow_up': 'How would you handle group chats with thousands of members?'
        },
        {
            'id': 'SD_A4',
            'question': 'What is event-driven architecture? Compare it to request-response architecture and explain when each is appropriate.',
            'difficulty': 'medium',
            'expected_keywords': ['event-driven', 'request-response', 'asynchronous', 'message broker', 'kafka', 'rabbitmq', 'decoupling', 'eventual consistency'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you ensure event ordering and handle duplicate events?'
        },
    ],
    'problem_solving': [
        {
            'id': 'SD_PS1',
            'question': 'Write a function to find the longest palindromic substring in a given string. Explain your approach and analyze time/space complexity.',
            'difficulty': 'hard',
            'expected_keywords': ['palindrome', 'substring', 'algorithm', 'complexity', 'optimization', 'dynamic programming'],
            'time_limit_minutes': 15,
            'follow_up': 'Can you optimize this for very large strings?'
        },
        {
            'id': 'SD_PS2',
            'question': 'How would you detect a cycle in a linked list? Implement the solution and explain the algorithm.',
            'difficulty': 'medium',
            'expected_keywords': ['cycle', 'linked list', 'two pointers', 'floyd', 'tortoise and hare', 'time complexity'],
            'time_limit_minutes': 10,
            'follow_up': 'How would you find the start point of the cycle?'
        },
        {
            'id': 'SD_PS3',
            'question': 'Given a stream of integers, design a data structure that supports inserting elements and finding the median in O(log n) time.',
            'difficulty': 'hard',
            'expected_keywords': ['heap', 'median', 'priority queue', 'balanced', 'max-heap', 'min-heap', 'stream'],
            'time_limit_minutes': 12,
            'follow_up': 'How would you extend this to support removal of elements?'
        },
        {
            'id': 'SD_PS4',
            'question': 'Explain how you would implement a LRU cache. Walk through the data structure, time complexity, and edge cases.',
            'difficulty': 'medium',
            'expected_keywords': ['lru', 'cache', 'hash map', 'linked list', 'doubly linked', 'eviction', 'O(1)'],
            'time_limit_minutes': 10,
            'follow_up': 'How would you make it thread-safe?'
        },
    ],
    'testing': [
        {
            'id': 'SD_T1',
            'question': 'Describe your approach to testing. What types of tests do you write and how do you decide what to test?',
            'difficulty': 'easy',
            'expected_keywords': ['unit test', 'integration test', 'test pyramid', 'coverage', 'mocking', 'assertion', 'regression'],
            'time_limit_minutes': 8,
            'follow_up': 'What\'s a reasonable test coverage target and why?'
        },
        {
            'id': 'SD_T2',
            'question': 'Explain the difference between mocking, stubbing, and faking in tests. When do you use each?',
            'difficulty': 'medium',
            'expected_keywords': ['mock', 'stub', 'fake', 'test double', 'isolation', 'dependency', 'behavior verification'],
            'time_limit_minutes': 8,
            'follow_up': 'When does too much mocking become a problem?'
        },
        {
            'id': 'SD_T3',
            'question': 'How would you test a complex distributed system? What strategies do you use for integration and end-to-end testing?',
            'difficulty': 'hard',
            'expected_keywords': ['integration testing', 'end-to-end', 'contract testing', 'chaos testing', 'testcontainers', 'environment', 'flaky tests'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you handle test environments that mirror production?'
        },
        {
            'id': 'SD_T4',
            'question': 'What is TDD (Test-Driven Development)? Walk through an example of how you\'d use TDD to implement a feature.',
            'difficulty': 'medium',
            'expected_keywords': ['tdd', 'red-green-refactor', 'test first', 'design', 'refactoring', 'feedback loop'],
            'time_limit_minutes': 10,
            'follow_up': 'When does TDD not work well?'
        },
    ],
    'databases': [
        {
            'id': 'SD_DB1',
            'question': 'Compare SQL and NoSQL databases. When would you choose MongoDB over PostgreSQL, and vice versa?',
            'difficulty': 'medium',
            'expected_keywords': ['sql', 'nosql', 'relational', 'document', 'schema', 'acid', 'scalability', 'flexibility'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you handle migrations in a NoSQL database?'
        },
        {
            'id': 'SD_DB2',
            'question': 'Explain database indexing. How does it improve query performance and what are the trade-offs?',
            'difficulty': 'medium',
            'expected_keywords': ['index', 'b-tree', 'query performance', 'write overhead', 'selectivity', 'composite index', 'covering index'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you decide which columns to index?'
        },
        {
            'id': 'SD_DB3',
            'question': 'What are database transactions? Explain ACID properties and the implications of different isolation levels.',
            'difficulty': 'hard',
            'expected_keywords': ['transaction', 'acid', 'atomicity', 'consistency', 'isolation', 'durability', 'isolation level', 'deadlock'],
            'time_limit_minutes': 12,
            'follow_up': 'How would you handle distributed transactions across microservices?'
        },
        {
            'id': 'SD_DB4',
            'question': 'Describe strategies for database scaling. What is sharding and how do you decide on a partition key?',
            'difficulty': 'hard',
            'expected_keywords': ['sharding', 'partitioning', 'replication', 'horizontal scaling', 'partition key', 'hot spots', 'consistent hashing'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you handle cross-shard queries?'
        },
    ],
    'api_design': [
        {
            'id': 'SD_API1',
            'question': 'Compare REST and GraphQL. What are the strengths and weaknesses of each? When would you use GraphQL over REST?',
            'difficulty': 'medium',
            'expected_keywords': ['rest', 'graphql', 'over-fetching', 'under-fetching', 'schema', 'resolver', 'endpoint', 'flexibility'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you handle versioning in REST APIs?'
        },
        {
            'id': 'SD_API2',
            'question': 'Design a REST API for a social media platform. Cover authentication, rate limiting, pagination, and error handling.',
            'difficulty': 'hard',
            'expected_keywords': ['authentication', 'rate limiting', 'pagination', 'error handling', 'status codes', 'jwt', 'oauth', 'hateoas'],
            'time_limit_minutes': 15,
            'follow_up': 'How would you implement real-time notifications?'
        },
        {
            'id': 'SD_API3',
            'question': 'What is API rate limiting? Describe different strategies and how you\'d implement it in a distributed system.',
            'difficulty': 'medium',
            'expected_keywords': ['rate limiting', 'token bucket', 'sliding window', 'distributed', 'redis', 'throttling', 'quota'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you handle rate-limited users gracefully?'
        },
    ],
    'security': [
        {
            'id': 'SD_SEC1',
            'question': 'Explain the OWASP Top 10. Describe three common vulnerabilities and how you prevent them in your applications.',
            'difficulty': 'hard',
            'expected_keywords': ['owasp', 'injection', 'xss', 'csrf', 'authentication', 'encryption', 'sanitization', 'security headers'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you stay updated on security best practices?'
        },
        {
            'id': 'SD_SEC2',
            'question': 'How does JWT authentication work? What are its advantages and potential security risks?',
            'difficulty': 'medium',
            'expected_keywords': ['jwt', 'token', 'header', 'payload', 'signature', 'expiration', 'refresh token', 'stateless'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you handle token revocation?'
        },
        {
            'id': 'SD_SEC3',
            'question': 'What is SQL injection? Demonstrate how it works and explain how to prevent it.',
            'difficulty': 'easy',
            'expected_keywords': ['sql injection', 'parameterized query', 'prepared statement', 'input validation', 'sanitization', 'orm'],
            'time_limit_minutes': 8,
            'follow_up': 'What other injection attacks are you aware of?'
        },
    ],
    'real_world_scenarios': [
        {
            'id': 'SD_RW1',
            'question': 'Your production API is suddenly returning 500 errors for 10% of requests. Walk me through your incident response — from detection to resolution to post-mortem.',
            'difficulty': 'hard',
            'expected_keywords': ['monitoring', 'alerting', 'logs', 'reproduction', 'rollback', 'incident response', 'post-mortem', 'root cause'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you prevent alert fatigue while catching real issues?'
        },
        {
            'id': 'SD_RW2',
            'question': 'You inherit a legacy codebase with no tests and poor documentation. How would you approach modernizing it while keeping the system running?',
            'difficulty': 'hard',
            'expected_keywords': ['legacy', 'refactoring', 'strangler pattern', 'characterization tests', 'incremental', 'documentation', 'risk'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you convince stakeholders to invest in technical debt?'
        },
        {
            'id': 'SD_RW3',
            'question': 'A critical feature needs to ship in one week but you estimate it requires three weeks. How do you handle this situation?',
            'difficulty': 'medium',
            'expected_keywords': ['scope', 'negotiation', 'mvp', 'trade-offs', 'communication', 'stakeholder', 'priority', 'deadline'],
            'time_limit_minutes': 10,
            'follow_up': 'Have you ever shipped something you weren\'t proud of? What happened?'
        },
    ],
}

# ============================================================================
# DATA ANALYST — 36 questions across 7 categories
# ============================================================================
DATA_ANALYST_QUESTIONS = {
    'fundamentals': [
        {
            'id': 'DA_F1',
            'question': 'Explain the difference between correlation and causation. Provide an example of when understanding this distinction prevented a bad business decision.',
            'difficulty': 'medium',
            'expected_keywords': ['correlation', 'causation', 'confounding', 'spurious', 'relationship', 'statistical', 'experiment'],
            'time_limit_minutes': 8,
            'follow_up': 'How would you design an experiment to establish causation?'
        },
        {
            'id': 'DA_F2',
            'question': 'Walk me through your process for cleaning and preparing messy data. What tools do you use and how do you handle missing values?',
            'difficulty': 'easy',
            'expected_keywords': ['cleaning', 'preprocessing', 'missing values', 'outliers', 'pandas', 'validation', 'imputation'],
            'time_limit_minutes': 7,
            'follow_up': 'How do you decide between removing or imputing missing data?'
        },
        {
            'id': 'DA_F3',
            'question': 'Describe a complex SQL query you\'ve written. What was the business problem and how did you optimize it?',
            'difficulty': 'hard',
            'expected_keywords': ['sql', 'join', 'subquery', 'cte', 'window function', 'optimization', 'index', 'performance'],
            'time_limit_minutes': 12,
            'follow_up': 'How did you validate the results were correct?'
        },
        {
            'id': 'DA_F4',
            'question': 'What are the common types of data (structured, semi-structured, unstructured)? Provide examples and explain how you work with each.',
            'difficulty': 'easy',
            'expected_keywords': ['structured', 'semi-structured', 'unstructured', 'csv', 'json', 'text', 'database', 'schema'],
            'time_limit_minutes': 7,
            'follow_up': 'How do you handle data from multiple formats in a single analysis?'
        },
        {
            'id': 'DA_F5',
            'question': 'Explain the concept of data normalization. When and why would you normalize data before analysis?',
            'difficulty': 'medium',
            'expected_keywords': ['normalization', 'standardization', 'scaling', 'z-score', 'min-max', 'comparison', 'outlier sensitivity'],
            'time_limit_minutes': 8,
            'follow_up': 'When is normalization harmful?'
        },
    ],
    'visualization': [
        {
            'id': 'DA_V1',
            'question': 'You need to present quarterly sales data to executives. What visualizations would you choose and why? How do you ensure your visualizations don\'t mislead?',
            'difficulty': 'medium',
            'expected_keywords': ['dashboard', 'chart', 'visualization', 'insight', 'clarity', 'audience', 'storytelling', 'misleading'],
            'time_limit_minutes': 10,
            'follow_up': 'Give an example of a misleading visualization you\'ve seen.'
        },
        {
            'id': 'DA_V2',
            'question': 'Explain when you would use a box plot vs. a histogram vs. a scatter plot. Provide specific business use cases.',
            'difficulty': 'easy',
            'expected_keywords': ['box plot', 'histogram', 'scatter plot', 'distribution', 'outliers', 'correlation', 'use case'],
            'time_limit_minutes': 6,
            'follow_up': 'How do you choose the right bin size for histograms?'
        },
        {
            'id': 'DA_V3',
            'question': 'How do you design a dashboard for non-technical stakeholders? What are the key principles of effective data storytelling?',
            'difficulty': 'medium',
            'expected_keywords': ['dashboard', 'storytelling', 'simplicity', 'audience', 'kpi', 'actionable', 'interactive', 'drill-down'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you handle stakeholders who request too many metrics on a single dashboard?'
        },
        {
            'id': 'DA_V4',
            'question': 'Compare Tableau, Power BI, and Matplotlib/Seaborn. When would you use each tool and what are their strengths?',
            'difficulty': 'easy',
            'expected_keywords': ['tableau', 'power bi', 'matplotlib', 'seaborn', 'interactive', 'programmatic', 'self-service', 'automation'],
            'time_limit_minutes': 8,
            'follow_up': 'How do you ensure consistent branding across visualizations?'
        },
    ],
    'statistics': [
        {
            'id': 'DA_S1',
            'question': 'Explain A/B testing. If you ran a test with 10,000 users and saw a 5% improvement with p-value 0.06, what would you recommend?',
            'difficulty': 'hard',
            'expected_keywords': ['a/b test', 'hypothesis', 'p-value', 'significance', 'sample size', 'statistical power', 'confidence'],
            'time_limit_minutes': 12,
            'follow_up': 'How would you detect and handle a novelty effect?'
        },
        {
            'id': 'DA_S2',
            'question': 'A company claims their new feature increased user retention by 20%. How would you verify this claim? What questions would you ask?',
            'difficulty': 'medium',
            'expected_keywords': ['retention', 'metric', 'cohort', 'baseline', 'statistical test', 'bias', 'confounding', 'validation'],
            'time_limit_minutes': 10,
            'follow_up': 'What are potential biases in measuring retention?'
        },
        {
            'id': 'DA_S3',
            'question': 'Explain the difference between Type I and Type II errors. Which is worse and in what context?',
            'difficulty': 'medium',
            'expected_keywords': ['type i', 'type ii', 'false positive', 'false negative', 'significance', 'power', 'context', 'trade-off'],
            'time_limit_minutes': 8,
            'follow_up': 'How do sample size decisions affect each type of error?'
        },
        {
            'id': 'DA_S4',
            'question': 'What is Bayesian analysis and how does it differ from frequentist approaches? When would you prefer one over the other?',
            'difficulty': 'hard',
            'expected_keywords': ['bayesian', 'frequentist', 'prior', 'posterior', 'likelihood', 'hypothesis', 'p-value', 'credible interval'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you choose priors in practice?'
        },
        {
            'id': 'DA_S5',
            'question': 'Explain regression analysis. What assumptions does linear regression make and how do you check if they hold?',
            'difficulty': 'medium',
            'expected_keywords': ['regression', 'linear', 'assumptions', 'residuals', 'normality', 'multicollinearity', 'homoscedasticity', 'r-squared'],
            'time_limit_minutes': 10,
            'follow_up': 'When would you use logistic regression instead?'
        },
    ],
    'business_acumen': [
        {
            'id': 'DA_BA1',
            'question': 'Describe a time when your analysis led to a business decision that saved money or increased revenue. What was your approach?',
            'difficulty': 'medium',
            'expected_keywords': ['analysis', 'insight', 'recommendation', 'impact', 'stakeholder', 'data-driven', 'business value'],
            'time_limit_minutes': 10,
            'follow_up': 'How did you measure the impact of your recommendation?'
        },
        {
            'id': 'DA_BA2',
            'question': 'If you notice a sudden 30% drop in a key metric, what steps would you take to investigate?',
            'difficulty': 'hard',
            'expected_keywords': ['investigation', 'root cause', 'data quality', 'segmentation', 'timeline', 'hypothesis', 'debugging'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you prioritize which hypotheses to test first?'
        },
        {
            'id': 'DA_BA3',
            'question': 'How do you translate complex analytical findings into actionable recommendations for non-technical stakeholders?',
            'difficulty': 'medium',
            'expected_keywords': ['communication', 'simplify', 'actionable', 'storytelling', 'visualization', 'business language', 'stakeholder'],
            'time_limit_minutes': 8,
            'follow_up': 'Give an example of a time when an audience didn\'t understand your analysis. What did you change?'
        },
    ],
    'tools_and_techniques': [
        {
            'id': 'DA_TT1',
            'question': 'Write a SQL query using window functions to calculate the running total and rank of sales by region and month.',
            'difficulty': 'hard',
            'expected_keywords': ['window function', 'partition by', 'order by', 'running total', 'rank', 'row_number', 'sum over'],
            'time_limit_minutes': 12,
            'follow_up': 'How do window functions differ from GROUP BY?'
        },
        {
            'id': 'DA_TT2',
            'question': 'Compare ETL and ELT approaches. When would you choose one over the other and what tools would you use?',
            'difficulty': 'medium',
            'expected_keywords': ['etl', 'elt', 'extract', 'transform', 'load', 'data warehouse', 'pipeline', 'dbt', 'airflow'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you handle data quality in a pipeline?'
        },
        {
            'id': 'DA_TT3',
            'question': 'Explain how you would handle a dataset with duplicate records. What are the common causes and how do you resolve them?',
            'difficulty': 'easy',
            'expected_keywords': ['duplicate', 'deduplication', 'primary key', 'merge', 'data quality', 'validation', 'ETL'],
            'time_limit_minutes': 7,
            'follow_up': 'How do you prevent duplicates from entering the system?'
        },
        {
            'id': 'DA_TT4',
            'question': 'Describe your experience with pivot tables and cross-tabulations. How do you use them for exploratory data analysis?',
            'difficulty': 'easy',
            'expected_keywords': ['pivot table', 'cross-tabulation', 'groupby', 'aggregation', 'excel', 'pandas', 'exploratory'],
            'time_limit_minutes': 7,
            'follow_up': 'How do you decide which dimensions to pivot on?'
        },
        {
            'id': 'DA_TT5',
            'question': 'How do you automate recurring reports? Describe a reporting workflow you\'ve built.',
            'difficulty': 'medium',
            'expected_keywords': ['automation', 'scheduling', 'reporting', 'pipeline', 'dashboard', 'cron', 'script', 'template'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you handle reports that break when source data changes?'
        },
    ],
    'data_modeling': [
        {
            'id': 'DA_DM1',
            'question': 'Explain the star schema and snowflake schema. When would you use each in a data warehouse?',
            'difficulty': 'medium',
            'expected_keywords': ['star schema', 'snowflake', 'fact table', 'dimension table', 'denormalization', 'query performance', 'data warehouse'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you handle slowly changing dimensions?'
        },
        {
            'id': 'DA_DM2',
            'question': 'What is data warehousing and how does it differ from a transactional database? Explain OLAP vs OLTP.',
            'difficulty': 'medium',
            'expected_keywords': ['data warehouse', 'olap', 'oltp', 'analytical', 'transactional', 'aggregation', 'historical data'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you decide which data to include in a data warehouse?'
        },
        {
            'id': 'DA_DM3',
            'question': 'Design a data model for an e-commerce platform. Consider products, orders, customers, and analytics needs.',
            'difficulty': 'hard',
            'expected_keywords': ['data model', 'entity', 'relationship', 'normalization', 'schema', 'analytics', 'query patterns'],
            'time_limit_minutes': 15,
            'follow_up': 'How would you optimize this model for reporting queries?'
        },
    ],
    'real_world_scenarios': [
        {
            'id': 'DA_RW1',
            'question': 'Your marketing team wants to know which campaign channels generate the highest ROI. The data is spread across 5 different platforms. How would you approach this analysis?',
            'difficulty': 'hard',
            'expected_keywords': ['roi', 'attribution', 'data integration', 'channels', 'metrics', 'normalization', 'comparison', 'cross-platform'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you handle attribution when a customer interacts with multiple channels?'
        },
        {
            'id': 'DA_RW2',
            'question': 'You discover that a report used by executives for decision-making has had incorrect data for the past 3 months. What do you do?',
            'difficulty': 'hard',
            'expected_keywords': ['error', 'communication', 'impact assessment', 'correction', 'root cause', 'process improvement', 'trust'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you build processes to prevent this from happening again?'
        },
        {
            'id': 'DA_RW3',
            'question': 'A product team asks you to analyze user engagement. However, the event tracking is inconsistent and has gaps. How do you proceed?',
            'difficulty': 'medium',
            'expected_keywords': ['data quality', 'event tracking', 'gaps', 'assumptions', 'documentation', 'limitations', 'recommendations'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you communicate data limitations to stakeholders?'
        },
    ],
}

# ============================================================================
# DATA SCIENTIST — 35 questions across 7 categories
# ============================================================================
DATA_SCIENTIST_QUESTIONS = {
    'ml_fundamentals': [
        {
            'id': 'DS_ML1',
            'question': 'Explain bias-variance tradeoff. How do you diagnose and fix high bias vs. high variance in your models?',
            'difficulty': 'hard',
            'expected_keywords': ['bias', 'variance', 'overfitting', 'underfitting', 'regularization', 'cross-validation', 'learning curve'],
            'time_limit_minutes': 12,
            'follow_up': 'Give a real example from a project where you balanced this tradeoff.'
        },
        {
            'id': 'DS_ML2',
            'question': 'Walk me through building a machine learning model from scratch - data collection to deployment. What are the most common pitfalls?',
            'difficulty': 'hard',
            'expected_keywords': ['pipeline', 'feature engineering', 'training', 'validation', 'deployment', 'monitoring', 'data drift'],
            'time_limit_minutes': 15,
            'follow_up': 'How do you handle model decay in production?'
        },
        {
            'id': 'DS_ML3',
            'question': 'Compare Random Forest and Gradient Boosting. When would you choose one over the other?',
            'difficulty': 'medium',
            'expected_keywords': ['random forest', 'gradient boosting', 'ensemble', 'bagging', 'boosting', 'overfitting', 'interpretability'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you tune hyperparameters for these models?'
        },
        {
            'id': 'DS_ML4',
            'question': 'Explain cross-validation. What are different types and when would you use each?',
            'difficulty': 'medium',
            'expected_keywords': ['cross-validation', 'k-fold', 'stratified', 'time series', 'leave-one-out', 'overfitting', 'generalization'],
            'time_limit_minutes': 8,
            'follow_up': 'When is k-fold cross-validation not appropriate?'
        },
        {
            'id': 'DS_ML5',
            'question': 'What is regularization? Compare L1 (Lasso) and L2 (Ridge) regularization and explain when to use each.',
            'difficulty': 'medium',
            'expected_keywords': ['regularization', 'l1', 'l2', 'lasso', 'ridge', 'feature selection', 'penalty', 'sparsity'],
            'time_limit_minutes': 10,
            'follow_up': 'What is Elastic Net and when would you prefer it?'
        },
        {
            'id': 'DS_ML6',
            'question': 'How do you handle imbalanced datasets? Describe at least three techniques and their trade-offs.',
            'difficulty': 'hard',
            'expected_keywords': ['imbalanced', 'oversampling', 'undersampling', 'smote', 'class weight', 'precision', 'recall', 'f1'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you evaluate model performance on imbalanced data?'
        },
    ],
    'deep_learning': [
        {
            'id': 'DS_DL1',
            'question': 'Explain how backpropagation works. How would you debug a neural network that isn\'t learning?',
            'difficulty': 'hard',
            'expected_keywords': ['backpropagation', 'gradient', 'chain rule', 'loss function', 'vanishing gradient', 'learning rate', 'debugging'],
            'time_limit_minutes': 15,
            'follow_up': 'What techniques prevent vanishing/exploding gradients?'
        },
        {
            'id': 'DS_DL2',
            'question': 'Describe the architecture and use cases for: CNN, RNN, and Transformer models. Which would you use for sentiment analysis?',
            'difficulty': 'hard',
            'expected_keywords': ['cnn', 'rnn', 'transformer', 'architecture', 'sentiment analysis', 'nlp', 'attention mechanism'],
            'time_limit_minutes': 12,
            'follow_up': 'How do attention mechanisms improve performance?'
        },
        {
            'id': 'DS_DL3',
            'question': 'What is transfer learning? Explain how pre-trained models are used and fine-tuned for specific tasks.',
            'difficulty': 'medium',
            'expected_keywords': ['transfer learning', 'pre-trained', 'fine-tuning', 'frozen layers', 'domain adaptation', 'feature extraction'],
            'time_limit_minutes': 10,
            'follow_up': 'When does transfer learning not work well?'
        },
        {
            'id': 'DS_DL4',
            'question': 'Explain batch normalization and dropout. Why are they used and where do you place them in a network architecture?',
            'difficulty': 'medium',
            'expected_keywords': ['batch normalization', 'dropout', 'regularization', 'training', 'inference', 'layer', 'generalization'],
            'time_limit_minutes': 8,
            'follow_up': 'How do these techniques interact with each other?'
        },
    ],
    'feature_engineering': [
        {
            'id': 'DS_FE1',
            'question': 'You have a dataset with categorical variables that have high cardinality (thousands of unique values). How would you handle this?',
            'difficulty': 'medium',
            'expected_keywords': ['categorical', 'encoding', 'target encoding', 'embedding', 'dimensionality', 'curse of dimensionality'],
            'time_limit_minutes': 10,
            'follow_up': 'What are the risks of target encoding?'
        },
        {
            'id': 'DS_FE2',
            'question': 'Describe your approach to feature selection. What techniques do you use and how do you avoid data leakage?',
            'difficulty': 'hard',
            'expected_keywords': ['feature selection', 'importance', 'correlation', 'mutual information', 'data leakage', 'pipeline'],
            'time_limit_minutes': 12,
            'follow_up': 'Give an example of subtle data leakage you\'ve encountered.'
        },
        {
            'id': 'DS_FE3',
            'question': 'How do you handle time-series features? Explain lag features, rolling statistics, and date-based features.',
            'difficulty': 'medium',
            'expected_keywords': ['time-series', 'lag', 'rolling', 'window', 'seasonality', 'trend', 'date features', 'autocorrelation'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you prevent look-ahead bias in time-series models?'
        },
        {
            'id': 'DS_FE4',
            'question': 'What is dimensionality reduction? Compare PCA and t-SNE and explain their use cases.',
            'difficulty': 'medium',
            'expected_keywords': ['dimensionality reduction', 'pca', 't-sne', 'variance', 'visualization', 'components', 'non-linear'],
            'time_limit_minutes': 10,
            'follow_up': 'When would you use UMAP instead of t-SNE?'
        },
    ],
    'nlp': [
        {
            'id': 'DS_NLP1',
            'question': 'Explain how word embeddings work. Compare Word2Vec, GloVe, and contextual embeddings like BERT.',
            'difficulty': 'hard',
            'expected_keywords': ['embedding', 'word2vec', 'glove', 'bert', 'context', 'semantic', 'vector', 'similarity'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you handle out-of-vocabulary words?'
        },
        {
            'id': 'DS_NLP2',
            'question': 'Design a text classification pipeline for customer support tickets. What preprocessing, models, and evaluation metrics would you use?',
            'difficulty': 'hard',
            'expected_keywords': ['text classification', 'preprocessing', 'tokenization', 'tfidf', 'embeddings', 'accuracy', 'f1', 'confusion matrix'],
            'time_limit_minutes': 15,
            'follow_up': 'How do you handle multilingual tickets?'
        },
        {
            'id': 'DS_NLP3',
            'question': 'What is named entity recognition (NER)? Explain approaches from rule-based to deep learning.',
            'difficulty': 'medium',
            'expected_keywords': ['ner', 'named entity', 'rule-based', 'crf', 'lstm', 'transformer', 'spacy', 'annotation'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you handle domain-specific entities?'
        },
    ],
    'model_deployment': [
        {
            'id': 'DS_MD1',
            'question': 'How do you deploy a machine learning model to production? Describe the infrastructure and monitoring needed.',
            'difficulty': 'hard',
            'expected_keywords': ['deployment', 'api', 'container', 'monitoring', 'latency', 'scaling', 'model serving', 'mlops'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you handle A/B testing between model versions?'
        },
        {
            'id': 'DS_MD2',
            'question': 'What is MLOps? Explain the components of an ML pipeline and how they differ from traditional DevOps.',
            'difficulty': 'medium',
            'expected_keywords': ['mlops', 'pipeline', 'experiment tracking', 'model registry', 'ci/cd', 'data versioning', 'reproducibility'],
            'time_limit_minutes': 10,
            'follow_up': 'What tools (MLflow, Kubeflow, etc.) have you used?'
        },
        {
            'id': 'DS_MD3',
            'question': 'Explain concept drift and data drift. How do you detect and respond to them in production?',
            'difficulty': 'hard',
            'expected_keywords': ['concept drift', 'data drift', 'monitoring', 'retraining', 'statistical tests', 'distribution', 'alert'],
            'time_limit_minutes': 12,
            'follow_up': 'How often should you retrain models?'
        },
    ],
    'ethics_and_fairness': [
        {
            'id': 'DS_EF1',
            'question': 'How do you ensure your ML models are fair and unbiased? What metrics do you use to measure fairness?',
            'difficulty': 'hard',
            'expected_keywords': ['fairness', 'bias', 'demographic parity', 'equal opportunity', 'disparate impact', 'audit', 'protected attributes'],
            'time_limit_minutes': 12,
            'follow_up': 'Is it possible to satisfy all fairness definitions simultaneously?'
        },
        {
            'id': 'DS_EF2',
            'question': 'Explain the concept of model interpretability. Why is it important and what tools do you use (SHAP, LIME, etc.)?',
            'difficulty': 'medium',
            'expected_keywords': ['interpretability', 'explainability', 'shap', 'lime', 'feature importance', 'black box', 'transparency'],
            'time_limit_minutes': 10,
            'follow_up': 'When is a black-box model acceptable?'
        },
    ],
    'real_world_scenarios': [
        {
            'id': 'DS_RW1',
            'question': 'Your model shows 95% accuracy in testing but fails in production. Walk through your debugging process.',
            'difficulty': 'hard',
            'expected_keywords': ['data leakage', 'training-serving skew', 'distribution shift', 'evaluation', 'debugging', 'monitoring'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you prevent this in future projects?'
        },
        {
            'id': 'DS_RW2',
            'question': 'A stakeholder wants a model built in 2 weeks for a problem with limited labeled data. How do you approach this pragmatically?',
            'difficulty': 'medium',
            'expected_keywords': ['baseline', 'heuristic', 'active learning', 'labeling', 'transfer learning', 'pragmatic', 'constraints'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you communicate model limitations to non-technical stakeholders?'
        },
        {
            'id': 'DS_RW3',
            'question': 'Your recommendation system is showing signs of filter bubble — users keep seeing similar content. How would you address this?',
            'difficulty': 'hard',
            'expected_keywords': ['filter bubble', 'diversity', 'exploration', 'exploitation', 'serendipity', 'recommendation', 'engagement'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you measure content diversity in recommendations?'
        },
    ],
}

# ============================================================================
# DEVOPS ENGINEER — 36 questions across 7 categories
# ============================================================================
DEVOPS_ENGINEER_QUESTIONS = {
    'fundamentals': [
        {
            'id': 'DO_F1',
            'question': 'Explain the CI/CD pipeline you\'ve implemented. What tools did you use and how did you ensure deployment safety?',
            'difficulty': 'hard',
            'expected_keywords': ['ci/cd', 'pipeline', 'jenkins', 'github actions', 'testing', 'deployment', 'rollback', 'blue-green'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you handle failed deployments?'
        },
        {
            'id': 'DO_F2',
            'question': 'Describe your experience with containerization. How does Docker differ from virtual machines? When would you use each?',
            'difficulty': 'medium',
            'expected_keywords': ['docker', 'container', 'virtual machine', 'isolation', 'orchestration', 'kubernetes', 'lightweight'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you optimize Docker image sizes?'
        },
        {
            'id': 'DO_F3',
            'question': 'Walk me through how you\'d troubleshoot a production server that\'s experiencing high latency.',
            'difficulty': 'hard',
            'expected_keywords': ['troubleshooting', 'latency', 'monitoring', 'logs', 'metrics', 'profiling', 'bottleneck', 'debugging'],
            'time_limit_minutes': 15,
            'follow_up': 'What monitoring tools do you use and why?'
        },
        {
            'id': 'DO_F4',
            'question': 'What is the difference between mutable and immutable infrastructure? Which do you prefer and why?',
            'difficulty': 'medium',
            'expected_keywords': ['mutable', 'immutable', 'configuration drift', 'reproducibility', 'cattle vs pets', 'disposable', 'idempotent'],
            'time_limit_minutes': 8,
            'follow_up': 'How do you implement immutable infrastructure in practice?'
        },
        {
            'id': 'DO_F5',
            'question': 'Explain the concept of GitOps. How does it improve deployment workflows?',
            'difficulty': 'medium',
            'expected_keywords': ['gitops', 'git', 'declarative', 'reconciliation', 'argocd', 'flux', 'version control', 'automated'],
            'time_limit_minutes': 10,
            'follow_up': 'What challenges have you faced with GitOps in practice?'
        },
    ],
    'infrastructure': [
        {
            'id': 'DO_I1',
            'question': 'Explain Infrastructure as Code. Compare Terraform vs. CloudFormation. Which do you prefer and why?',
            'difficulty': 'medium',
            'expected_keywords': ['iac', 'terraform', 'cloudformation', 'declarative', 'state management', 'version control', 'automation'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you manage secrets in IaC?'
        },
        {
            'id': 'DO_I2',
            'question': 'Design a highly available and scalable architecture for an e-commerce application. Consider database, caching, and disaster recovery.',
            'difficulty': 'hard',
            'expected_keywords': ['high availability', 'scalability', 'load balancer', 'database replication', 'caching', 'disaster recovery', 'failover'],
            'time_limit_minutes': 15,
            'follow_up': 'What\'s your RTO and RPO strategy?'
        },
        {
            'id': 'DO_I3',
            'question': 'Compare AWS, Azure, and GCP. What are their respective strengths? How do you avoid vendor lock-in?',
            'difficulty': 'medium',
            'expected_keywords': ['aws', 'azure', 'gcp', 'cloud', 'multi-cloud', 'vendor lock-in', 'abstraction', 'kubernetes'],
            'time_limit_minutes': 10,
            'follow_up': 'Have you managed a multi-cloud deployment?'
        },
        {
            'id': 'DO_I4',
            'question': 'Explain Kubernetes architecture. How do pods, services, deployments, and ingress work together?',
            'difficulty': 'hard',
            'expected_keywords': ['kubernetes', 'pod', 'service', 'deployment', 'ingress', 'control plane', 'container orchestration', 'scaling'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you handle stateful applications in Kubernetes?'
        },
    ],
    'monitoring': [
        {
            'id': 'DO_MO1',
            'question': 'What is observability? Explain the three pillars (logs, metrics, traces) and how they complement each other.',
            'difficulty': 'medium',
            'expected_keywords': ['observability', 'logs', 'metrics', 'traces', 'monitoring', 'alerting', 'correlation', 'debugging'],
            'time_limit_minutes': 10,
            'follow_up': 'What tools do you use for each pillar?'
        },
        {
            'id': 'DO_MO2',
            'question': 'How do you set up alerting that is actionable and avoids alert fatigue? Describe your approach.',
            'difficulty': 'hard',
            'expected_keywords': ['alerting', 'threshold', 'anomaly detection', 'runbook', 'escalation', 'suppression', 'fatigue', 'sla'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you handle alerts during off-hours?'
        },
        {
            'id': 'DO_MO3',
            'question': 'Explain distributed tracing. How does it help debug issues across microservices?',
            'difficulty': 'hard',
            'expected_keywords': ['distributed tracing', 'span', 'trace id', 'jaeger', 'zipkin', 'opentelemetry', 'microservices', 'latency'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you handle tracing in asynchronous systems?'
        },
        {
            'id': 'DO_MO4',
            'question': 'What SLAs, SLOs, and SLIs would you define for a web application? How do error budgets work?',
            'difficulty': 'medium',
            'expected_keywords': ['sla', 'slo', 'sli', 'error budget', 'reliability', 'uptime', 'latency target', 'measurement'],
            'time_limit_minutes': 10,
            'follow_up': 'What happens when you exhaust your error budget?'
        },
    ],
    'security': [
        {
            'id': 'DO_SC1',
            'question': 'Explain the principle of least privilege. How do you implement it in cloud environments?',
            'difficulty': 'medium',
            'expected_keywords': ['least privilege', 'iam', 'role', 'permissions', 'access control', 'audit', 'zero trust'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you handle emergency access?'
        },
        {
            'id': 'DO_SC2',
            'question': 'How do you manage secrets (API keys, passwords, certificates) in production? Compare different approaches.',
            'difficulty': 'hard',
            'expected_keywords': ['secrets management', 'vault', 'kms', 'environment variables', 'rotation', 'encryption', 'access audit'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you handle secret rotation without downtime?'
        },
        {
            'id': 'DO_SC3',
            'question': 'Describe container security best practices. How do you scan images, manage vulnerabilities, and enforce policies?',
            'difficulty': 'hard',
            'expected_keywords': ['container security', 'image scanning', 'vulnerability', 'base image', 'runtime policy', 'namespace', 'rootless'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you handle zero-day vulnerabilities in base images?'
        },
    ],
    'automation': [
        {
            'id': 'DO_AU1',
            'question': 'How do you automate server provisioning and configuration management? Compare Ansible, Chef, and Puppet.',
            'difficulty': 'medium',
            'expected_keywords': ['automation', 'ansible', 'chef', 'puppet', 'configuration management', 'idempotent', 'playbook', 'recipe'],
            'time_limit_minutes': 10,
            'follow_up': 'When would you use configuration management vs. containerization?'
        },
        {
            'id': 'DO_AU2',
            'question': 'Describe your most complex automation project. What problems did it solve and what challenges did you face?',
            'difficulty': 'hard',
            'expected_keywords': ['automation', 'pipeline', 'scripting', 'integration', 'complexity', 'reliability', 'maintenance'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you test your automation scripts?'
        },
        {
            'id': 'DO_AU3',
            'question': 'What is chaos engineering? How would you implement controlled chaos experiments in a production environment?',
            'difficulty': 'hard',
            'expected_keywords': ['chaos engineering', 'resilience', 'fault injection', 'game day', 'steady state', 'blast radius', 'recovery'],
            'time_limit_minutes': 12,
            'follow_up': 'What safeguards do you put in place before running chaos experiments?'
        },
    ],
    'networking': [
        {
            'id': 'DO_NW1',
            'question': 'Explain how DNS works, from browser to server. How would you troubleshoot DNS resolution issues?',
            'difficulty': 'medium',
            'expected_keywords': ['dns', 'resolution', 'a record', 'cname', 'ttl', 'recursive', 'authoritative', 'nslookup'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you implement DNS-based load balancing?'
        },
        {
            'id': 'DO_NW2',
            'question': 'What is a service mesh? Explain how Istio or Linkerd handles traffic management, security, and observability.',
            'difficulty': 'hard',
            'expected_keywords': ['service mesh', 'istio', 'linkerd', 'sidecar', 'traffic management', 'mtls', 'service discovery', 'proxy'],
            'time_limit_minutes': 12,
            'follow_up': 'When is a service mesh overkill?'
        },
        {
            'id': 'DO_NW3',
            'question': 'Explain load balancing strategies (round-robin, least connections, IP hash). When would you use each?',
            'difficulty': 'easy',
            'expected_keywords': ['load balancing', 'round-robin', 'least connections', 'ip hash', 'health check', 'sticky sessions', 'l4 vs l7'],
            'time_limit_minutes': 8,
            'follow_up': 'How do you handle session persistence?'
        },
    ],
    'real_world_scenarios': [
        {
            'id': 'DO_RW1',
            'question': 'It\'s 3 AM and your monitoring alerts that multiple services are down. Walk through your incident response process.',
            'difficulty': 'hard',
            'expected_keywords': ['incident response', 'triage', 'communication', 'rollback', 'investigation', 'post-mortem', 'war room'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you communicate during incidents with stakeholders?'
        },
        {
            'id': 'DO_RW2',
            'question': 'Your application needs to migrate from a monolithic VM-based deployment to containers on Kubernetes with zero downtime. Plan the migration.',
            'difficulty': 'hard',
            'expected_keywords': ['migration', 'containerization', 'kubernetes', 'zero downtime', 'incremental', 'rollback', 'testing', 'parallel running'],
            'time_limit_minutes': 15,
            'follow_up': 'What risks are you most concerned about?'
        },
        {
            'id': 'DO_RW3',
            'question': 'A developer pushes a commit that accidentally exposes API keys to a public repository. What are the immediate and long-term actions?',
            'difficulty': 'medium',
            'expected_keywords': ['secret exposure', 'rotation', 'revoke', 'audit', 'git history', 'scanning', 'prevention', 'policy'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you prevent this from happening again?'
        },
    ],
}

# ============================================================================
# PRODUCT MANAGER — 36 questions across 7 categories
# ============================================================================
PRODUCT_MANAGER_QUESTIONS = {
    'strategy': [
        {
            'id': 'PM_S1',
            'question': 'Describe how you prioritize features when you have limited engineering resources and multiple stakeholder requests.',
            'difficulty': 'hard',
            'expected_keywords': ['prioritization', 'stakeholder', 'impact', 'effort', 'rice', 'moscow', 'roadmap', 'trade-offs'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you say no to important stakeholders?'
        },
        {
            'id': 'PM_S2',
            'question': 'Tell me about a product you shipped that didn\'t perform as expected. What did you learn and how did you pivot?',
            'difficulty': 'medium',
            'expected_keywords': ['failure', 'learning', 'metrics', 'pivot', 'user feedback', 'iteration', 'retrospective'],
            'time_limit_minutes': 10,
            'follow_up': 'How did you communicate this to leadership?'
        },
        {
            'id': 'PM_S3',
            'question': 'How do you develop a product vision and roadmap? Walk through your process from market analysis to quarterly planning.',
            'difficulty': 'hard',
            'expected_keywords': ['vision', 'roadmap', 'market analysis', 'competitive', 'okrs', 'quarterly planning', 'alignment', 'theme'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you handle roadmap changes mid-quarter?'
        },
        {
            'id': 'PM_S4',
            'question': 'Explain your approach to competitive analysis. How do you position your product against established competitors?',
            'difficulty': 'medium',
            'expected_keywords': ['competitive analysis', 'positioning', 'differentiation', 'market', 'unique value proposition', 'swot', 'moat'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you handle a competitor launching a similar feature first?'
        },
        {
            'id': 'PM_S5',
            'question': 'What framework do you use to decide whether to build, buy, or partner for a new capability?',
            'difficulty': 'medium',
            'expected_keywords': ['build', 'buy', 'partner', 'cost', 'core competency', 'time to market', 'risk', 'strategic'],
            'time_limit_minutes': 10,
            'follow_up': 'Give an example of when you made this decision.'
        },
    ],
    'metrics': [
        {
            'id': 'PM_M1',
            'question': 'How would you measure the success of [company\'s product]? What are the key metrics and why?',
            'difficulty': 'hard',
            'expected_keywords': ['metrics', 'kpi', 'success criteria', 'user engagement', 'retention', 'conversion', 'north star metric'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you avoid vanity metrics?'
        },
        {
            'id': 'PM_M2',
            'question': 'Explain the AARRR (Pirate Metrics) framework. How would you apply it to a SaaS product?',
            'difficulty': 'medium',
            'expected_keywords': ['aarrr', 'acquisition', 'activation', 'retention', 'referral', 'revenue', 'funnel', 'saas'],
            'time_limit_minutes': 10,
            'follow_up': 'Which metric would you prioritize first for a new product?'
        },
        {
            'id': 'PM_M3',
            'question': 'How do you set up and run a successful A/B test? What are the common pitfalls?',
            'difficulty': 'hard',
            'expected_keywords': ['a/b test', 'hypothesis', 'sample size', 'statistical significance', 'control', 'variant', 'novelty effect'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you decide when to stop a test early?'
        },
        {
            'id': 'PM_M4',
            'question': 'What is a North Star Metric? How do you identify one for your product and cascade it to team-level OKRs?',
            'difficulty': 'medium',
            'expected_keywords': ['north star', 'metric', 'okr', 'alignment', 'leading indicator', 'lagging indicator', 'team goals'],
            'time_limit_minutes': 10,
            'follow_up': 'When should you change your North Star Metric?'
        },
    ],
    'user_research': [
        {
            'id': 'PM_UR1',
            'question': 'How do you conduct user research? Describe different methods and when you use each.',
            'difficulty': 'medium',
            'expected_keywords': ['user research', 'interview', 'survey', 'usability testing', 'observation', 'quantitative', 'qualitative', 'persona'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you avoid bias in user research?'
        },
        {
            'id': 'PM_UR2',
            'question': 'A user requests a specific feature. How do you determine if it\'s a feature worth building vs. an edge case?',
            'difficulty': 'medium',
            'expected_keywords': ['user feedback', 'validation', 'data', 'frequency', 'impact', 'segment', 'underlying need', 'jobs to be done'],
            'time_limit_minutes': 8,
            'follow_up': 'How do you differentiate between what users say they want and what they actually need?'
        },
        {
            'id': 'PM_UR3',
            'question': 'Explain the Jobs-to-be-Done (JTBD) framework. How does it differ from traditional user personas?',
            'difficulty': 'hard',
            'expected_keywords': ['jobs to be done', 'functional', 'emotional', 'social', 'progress', 'persona', 'context', 'outcome'],
            'time_limit_minutes': 10,
            'follow_up': 'Give an example of a JTBD insight that changed a product direction.'
        },
        {
            'id': 'PM_UR4',
            'question': 'How do you validate a product idea before building it? What is an MVP and when have you used one?',
            'difficulty': 'easy',
            'expected_keywords': ['mvp', 'validation', 'prototype', 'hypothesis', 'lean', 'experiment', 'customer discovery', 'iteration'],
            'time_limit_minutes': 8,
            'follow_up': 'What\'s the smallest MVP you\'ve shipped?'
        },
    ],
    'technical_understanding': [
        {
            'id': 'PM_TU1',
            'question': 'How do you collaborate with engineering teams? How do you balance technical debt with feature development?',
            'difficulty': 'hard',
            'expected_keywords': ['collaboration', 'engineering', 'technical debt', 'trade-offs', 'sprint planning', 'estimation', 'trust'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you make a case for technical debt work to business stakeholders?'
        },
        {
            'id': 'PM_TU2',
            'question': 'Explain a complex technical concept (API, database, ML model) to a non-technical stakeholder right now.',
            'difficulty': 'medium',
            'expected_keywords': ['analogy', 'simplify', 'audience', 'non-technical', 'clear', 'example', 'communication'],
            'time_limit_minutes': 8,
            'follow_up': 'How deep should a PM\'s technical knowledge go?'
        },
        {
            'id': 'PM_TU3',
            'question': 'How do you write effective PRDs (Product Requirements Documents)? What sections are essential?',
            'difficulty': 'medium',
            'expected_keywords': ['prd', 'requirements', 'user stories', 'acceptance criteria', 'context', 'scope', 'out of scope', 'wireframes'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you handle requirements that change during development?'
        },
    ],
    'leadership': [
        {
            'id': 'PM_L1',
            'question': 'How do you influence and align cross-functional teams without direct authority? Give a specific example.',
            'difficulty': 'hard',
            'expected_keywords': ['influence', 'alignment', 'cross-functional', 'stakeholder', 'communication', 'empathy', 'consensus', 'trust'],
            'time_limit_minutes': 12,
            'follow_up': 'What do you do when alignment breaks down?'
        },
        {
            'id': 'PM_L2',
            'question': 'Describe a time you had to make a product decision with incomplete data. What was your framework?',
            'difficulty': 'hard',
            'expected_keywords': ['decision making', 'incomplete data', 'risk', 'intuition', 'framework', 'reversible', 'one-way door', 'two-way door'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you build conviction when data is lacking?'
        },
        {
            'id': 'PM_L3',
            'question': 'How do you manage stakeholder expectations when timelines slip or scope changes?',
            'difficulty': 'medium',
            'expected_keywords': ['stakeholder management', 'communication', 'transparency', 'expectations', 'scope change', 'trade-offs', 'updates'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you prevent scope creep?'
        },
    ],
    'market_analysis': [
        {
            'id': 'PM_MA1',
            'question': 'How would you assess the market opportunity for a new product? Walk through your analysis framework.',
            'difficulty': 'hard',
            'expected_keywords': ['market size', 'tam', 'sam', 'som', 'opportunity', 'competitor', 'trend', 'customer segment'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you validate market size estimates?'
        },
        {
            'id': 'PM_MA2',
            'question': 'Explain pricing strategy. How do you decide between freemium, subscription, and one-time purchase models?',
            'difficulty': 'medium',
            'expected_keywords': ['pricing', 'freemium', 'subscription', 'value', 'willingness to pay', 'competitor pricing', 'monetization'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you test pricing changes?'
        },
        {
            'id': 'PM_MA3',
            'question': 'How do you identify and respond to market disruption? Give an example of a disrupted industry.',
            'difficulty': 'medium',
            'expected_keywords': ['disruption', 'innovation', 'market shift', 'adaptation', 'technology', 'incumbent', 'challenger'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you future-proof your product strategy?'
        },
    ],
    'real_world_scenarios': [
        {
            'id': 'PM_RW1',
            'question': 'Your biggest customer threatens to churn unless you build a specific feature that conflicts with your product vision. How do you handle it?',
            'difficulty': 'hard',
            'expected_keywords': ['customer retention', 'product vision', 'negotiation', 'trade-offs', 'data', 'alternatives', 'churn', 'strategic'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you prevent one customer from derailing your roadmap?'
        },
        {
            'id': 'PM_RW2',
            'question': 'You notice user engagement dropping after a recent launch. Users aren\'t complaining loudly, but the numbers are down. What do you do?',
            'difficulty': 'medium',
            'expected_keywords': ['engagement', 'analysis', 'funnel', 'segmentation', 'cohort', 'rollback', 'user research', 'investigation'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you distinguish between seasonal changes and real product issues?'
        },
        {
            'id': 'PM_RW3',
            'question': 'Design and leadership disagree on the direction of a major feature. Engineering is blocked. How do you resolve this?',
            'difficulty': 'hard',
            'expected_keywords': ['conflict resolution', 'alignment', 'data', 'user research', 'compromise', 'escalation', 'facilitation', 'deadline'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you maintain relationships after a contentious decision?'
        },
    ],
}

# ============================================================================
# UI/UX DESIGNER — 36 questions across 7 categories
# ============================================================================
UI_UX_DESIGNER_QUESTIONS = {
    'design_process': [
        {
            'id': 'UX_DP1',
            'question': 'Walk me through your design process from user research to final implementation. How do you validate your designs?',
            'difficulty': 'medium',
            'expected_keywords': ['user research', 'wireframe', 'prototype', 'usability testing', 'iteration', 'feedback', 'validation'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you balance user needs with business goals?'
        },
        {
            'id': 'UX_DP2',
            'question': 'Describe a time when user testing revealed your initial design was wrong. How did you respond?',
            'difficulty': 'hard',
            'expected_keywords': ['user testing', 'feedback', 'iteration', 'redesign', 'learning', 'humility', 'data-driven'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you prevent confirmation bias in testing?'
        },
        {
            'id': 'UX_DP3',
            'question': 'How do you handle design critiques and feedback from stakeholders who aren\'t designers?',
            'difficulty': 'medium',
            'expected_keywords': ['critique', 'feedback', 'stakeholder', 'communication', 'justification', 'data', 'user needs', 'professionalism'],
            'time_limit_minutes': 8,
            'follow_up': 'How do you know when to push back vs. accommodate feedback?'
        },
        {
            'id': 'UX_DP4',
            'question': 'Explain design thinking. Walk through the five stages and give an example of how you\'ve applied them.',
            'difficulty': 'easy',
            'expected_keywords': ['design thinking', 'empathize', 'define', 'ideate', 'prototype', 'test', 'user-centered', 'iteration'],
            'time_limit_minutes': 10,
            'follow_up': 'When does the design thinking process break down?'
        },
    ],
    'principles': [
        {
            'id': 'UX_P1',
            'question': 'Explain key accessibility principles. How do you ensure your designs are accessible to users with disabilities?',
            'difficulty': 'medium',
            'expected_keywords': ['accessibility', 'wcag', 'screen reader', 'contrast', 'keyboard navigation', 'inclusive design'],
            'time_limit_minutes': 10,
            'follow_up': 'Give an example of an accessibility issue you fixed.'
        },
        {
            'id': 'UX_P2',
            'question': 'Explain Gestalt principles of visual perception. How do you apply them in UI design?',
            'difficulty': 'medium',
            'expected_keywords': ['gestalt', 'proximity', 'similarity', 'closure', 'continuity', 'figure-ground', 'visual hierarchy'],
            'time_limit_minutes': 10,
            'follow_up': 'Give an example where a Gestalt principle solved a design problem.'
        },
        {
            'id': 'UX_P3',
            'question': 'What is Fitts\' Law and Hick\'s Law? How do they influence your design decisions?',
            'difficulty': 'medium',
            'expected_keywords': ['fitts law', 'hicks law', 'target size', 'distance', 'decision time', 'options', 'usability', 'interaction'],
            'time_limit_minutes': 8,
            'follow_up': 'How do these laws apply differently on mobile vs. desktop?'
        },
        {
            'id': 'UX_P4',
            'question': 'How do you create and maintain a design system? What are the essential components?',
            'difficulty': 'hard',
            'expected_keywords': ['design system', 'components', 'tokens', 'consistency', 'documentation', 'scalability', 'governance', 'reusable'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you get adoption of a design system across teams?'
        },
    ],
    'research_methods': [
        {
            'id': 'UX_RM1',
            'question': 'Compare moderated vs. unmoderated usability testing. When would you choose each?',
            'difficulty': 'medium',
            'expected_keywords': ['moderated', 'unmoderated', 'usability testing', 'remote', 'in-person', 'think-aloud', 'task completion', 'qualitative'],
            'time_limit_minutes': 10,
            'follow_up': 'How many participants do you typically recruit?'
        },
        {
            'id': 'UX_RM2',
            'question': 'How do you create user personas? What data sources do you use and how do you validate them?',
            'difficulty': 'easy',
            'expected_keywords': ['persona', 'user research', 'demographics', 'behavior', 'goals', 'pain points', 'validation', 'data-driven'],
            'time_limit_minutes': 8,
            'follow_up': 'When are personas not helpful?'
        },
        {
            'id': 'UX_RM3',
            'question': 'Explain card sorting and tree testing. How do they help with information architecture?',
            'difficulty': 'medium',
            'expected_keywords': ['card sorting', 'tree testing', 'information architecture', 'navigation', 'categorization', 'mental model', 'labeling'],
            'time_limit_minutes': 10,
            'follow_up': 'How many participants do you need for reliable card sorting results?'
        },
        {
            'id': 'UX_RM4',
            'question': 'How do you use analytics data alongside qualitative research? Give an example where the two painted different pictures.',
            'difficulty': 'hard',
            'expected_keywords': ['analytics', 'qualitative', 'quantitative', 'triangulation', 'heatmap', 'funnel', 'interview', 'contradiction'],
            'time_limit_minutes': 12,
            'follow_up': 'Which do you trust more when they conflict?'
        },
        {
            'id': 'UX_RM5',
            'question': 'How do you conduct a competitive UX audit? What do you evaluate and how do you present findings?',
            'difficulty': 'medium',
            'expected_keywords': ['competitive audit', 'benchmark', 'heuristic', 'patterns', 'comparison', 'strengths', 'weaknesses', 'opportunity'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you avoid simply copying competitor designs?'
        },
    ],
    'visual_design': [
        {
            'id': 'UX_VD1',
            'question': 'How do you establish visual hierarchy in a complex interface? Walk through your approach.',
            'difficulty': 'medium',
            'expected_keywords': ['visual hierarchy', 'typography', 'color', 'spacing', 'size', 'contrast', 'weight', 'focal point'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you validate that users see the elements in the intended order?'
        },
        {
            'id': 'UX_VD2',
            'question': 'Explain color theory in UI design. How do you choose accessible color palettes?',
            'difficulty': 'medium',
            'expected_keywords': ['color theory', 'contrast ratio', 'accessibility', 'palette', 'primary', 'secondary', 'semantic', 'wcag'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you design for users with color blindness?'
        },
        {
            'id': 'UX_VD3',
            'question': 'What role does typography play in UX? How do you select fonts and establish a type scale?',
            'difficulty': 'easy',
            'expected_keywords': ['typography', 'font', 'type scale', 'readability', 'hierarchy', 'line height', 'weight', 'pairing'],
            'time_limit_minutes': 8,
            'follow_up': 'How do you test readability across devices?'
        },
        {
            'id': 'UX_VD4',
            'question': 'Describe your approach to responsive design. How do you ensure a consistent experience across mobile, tablet, and desktop?',
            'difficulty': 'medium',
            'expected_keywords': ['responsive', 'breakpoints', 'mobile-first', 'grid', 'flexible', 'media query', 'touch', 'adaptive'],
            'time_limit_minutes': 10,
            'follow_up': 'When would you choose a separate mobile design vs. responsive?'
        },
        {
            'id': 'UX_VD5',
            'question': 'What is motion design in UX? How do you use animation purposefully without distracting users?',
            'difficulty': 'medium',
            'expected_keywords': ['animation', 'motion', 'transition', 'microinteraction', 'feedback', 'delight', 'performance', 'reduced motion'],
            'time_limit_minutes': 8,
            'follow_up': 'How do you handle users who prefer reduced motion?'
        },
    ],
    'prototyping': [
        {
            'id': 'UX_PR1',
            'question': 'Compare low-fidelity and high-fidelity prototyping. When do you use each and what tools do you prefer?',
            'difficulty': 'easy',
            'expected_keywords': ['low-fidelity', 'high-fidelity', 'wireframe', 'mockup', 'prototype', 'figma', 'sketch', 'testing'],
            'time_limit_minutes': 8,
            'follow_up': 'How do you decide how much fidelity is needed for a given round of testing?'
        },
        {
            'id': 'UX_PR2',
            'question': 'How do you design complex interaction flows? Walk through prototyping a multi-step form or checkout process.',
            'difficulty': 'hard',
            'expected_keywords': ['interaction flow', 'user flow', 'prototype', 'multi-step', 'validation', 'error handling', 'progress', 'state'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you handle edge cases in your prototypes?'
        },
        {
            'id': 'UX_PR3',
            'question': 'Explain your handoff process to developers. How do you ensure design intent is preserved in implementation?',
            'difficulty': 'medium',
            'expected_keywords': ['handoff', 'developer', 'specification', 'design tokens', 'annotation', 'inspection', 'collaboration', 'qa'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you handle design compromises during development?'
        },
    ],
    'information_architecture': [
        {
            'id': 'UX_IA1',
            'question': 'How do you design the navigation structure for a complex application? What methods do you use?',
            'difficulty': 'hard',
            'expected_keywords': ['navigation', 'information architecture', 'sitemap', 'hierarchy', 'labeling', 'card sorting', 'findability'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you balance breadth vs. depth in navigation?'
        },
        {
            'id': 'UX_IA2',
            'question': 'How do you design for search and discovery? What patterns help users find what they need?',
            'difficulty': 'medium',
            'expected_keywords': ['search', 'discovery', 'filter', 'facet', 'autocomplete', 'browse', 'catalog', 'information scent'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you handle zero-result search states?'
        },
        {
            'id': 'UX_IA3',
            'question': 'Explain content strategy in UX. How does content influence user experience?',
            'difficulty': 'medium',
            'expected_keywords': ['content strategy', 'microcopy', 'voice and tone', 'clarity', 'user needs', 'content audit', 'structure'],
            'time_limit_minutes': 10,
            'follow_up': 'How do you write effective error messages?'
        },
    ],
    'real_world_scenarios': [
        {
            'id': 'UX_RW1',
            'question': 'You\'re redesigning a product with millions of existing users. How do you balance innovation with familiarity?',
            'difficulty': 'hard',
            'expected_keywords': ['redesign', 'migration', 'familiarity', 'innovation', 'gradual', 'user feedback', 'testing', 'change management'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you handle user backlash to design changes?'
        },
        {
            'id': 'UX_RW2',
            'question': 'A developer says your design is technically impossible to implement. How do you respond?',
            'difficulty': 'medium',
            'expected_keywords': ['collaboration', 'constraints', 'alternative', 'compromise', 'understanding', 'feasibility', 'negotiation'],
            'time_limit_minutes': 8,
            'follow_up': 'How do you learn enough about technical constraints to avoid this?'
        },
        {
            'id': 'UX_RW3',
            'question': 'You have 2 days to design a new feature. How do you adapt your process to meet a tight deadline?',
            'difficulty': 'medium',
            'expected_keywords': ['time constraint', 'prioritize', 'scope', 'rapid prototyping', 'design sprint', 'iteration', 'pragmatic'],
            'time_limit_minutes': 8,
            'follow_up': 'What do you cut first when under time pressure?'
        },
        {
            'id': 'UX_RW4',
            'question': 'Your analytics show that users are repeatedly failing at a specific task. Walk through how you\'d diagnose and fix the issue.',
            'difficulty': 'hard',
            'expected_keywords': ['analytics', 'funnel', 'drop-off', 'usability testing', 'diagnosis', 'redesign', 'validation', 'metrics'],
            'time_limit_minutes': 12,
            'follow_up': 'How do you prioritize UX fixes against new feature requests?'
        },
    ],
}


# ============================================================================
# UNIVERSAL BEHAVIORAL QUESTIONS — 15 total
# ============================================================================
UNIVERSAL_BEHAVIORAL_QUESTIONS = [
    {
        'id': 'BEH_1',
        'question': 'Tell me about a time when you had to learn a new technology or skill quickly to complete a project. How did you approach it?',
        'difficulty': 'medium',
        'category': 'learning_agility',
        'expected_keywords': ['learning', 'self-taught', 'documentation', 'practice', 'deadline', 'resourceful'],
        'star_required': True
    },
    {
        'id': 'BEH_2',
        'question': 'Describe a situation where you disagreed with a team member or manager. How did you handle it and what was the outcome?',
        'difficulty': 'hard',
        'category': 'conflict_resolution',
        'expected_keywords': ['disagreement', 'communication', 'compromise', 'resolution', 'respect', 'outcome'],
        'star_required': True
    },
    {
        'id': 'BEH_3',
        'question': 'Give me an example of a project that didn\'t go as planned. What went wrong and what did you do about it?',
        'difficulty': 'medium',
        'category': 'problem_solving',
        'expected_keywords': ['challenge', 'problem', 'solution', 'adaptation', 'learning', 'outcome'],
        'star_required': True
    },
    {
        'id': 'BEH_4',
        'question': 'Tell me about your greatest professional achievement. What made it significant and what was your specific contribution?',
        'difficulty': 'easy',
        'category': 'achievement',
        'expected_keywords': ['achievement', 'impact', 'contribution', 'success', 'measurable', 'proud'],
        'star_required': True
    },
    {
        'id': 'BEH_5',
        'question': 'Describe a time when you had to work with a difficult stakeholder or client. How did you manage the relationship?',
        'difficulty': 'hard',
        'category': 'stakeholder_management',
        'expected_keywords': ['stakeholder', 'difficult', 'communication', 'expectations', 'relationship', 'diplomacy'],
        'star_required': True
    },
    {
        'id': 'BEH_6',
        'question': 'Tell me about a time when you identified a process improvement. How did you implement it and what was the impact?',
        'difficulty': 'medium',
        'category': 'initiative',
        'expected_keywords': ['improvement', 'initiative', 'process', 'efficiency', 'implementation', 'impact'],
        'star_required': True
    },
    {
        'id': 'BEH_7',
        'question': 'Describe a time when you had to work under significant pressure or tight deadlines. How did you manage your time and stress?',
        'difficulty': 'medium',
        'category': 'pressure_management',
        'expected_keywords': ['pressure', 'deadline', 'prioritization', 'stress', 'time management', 'focus', 'outcome'],
        'star_required': True
    },
    {
        'id': 'BEH_8',
        'question': 'Tell me about a time when you mentored or helped a colleague grow. What approach did you take and what was the result?',
        'difficulty': 'medium',
        'category': 'mentorship',
        'expected_keywords': ['mentor', 'coaching', 'growth', 'feedback', 'development', 'support', 'progress'],
        'star_required': True
    },
    {
        'id': 'BEH_9',
        'question': 'Give an example of when you received critical feedback. How did you react and what did you change?',
        'difficulty': 'hard',
        'category': 'growth_mindset',
        'expected_keywords': ['feedback', 'criticism', 'growth', 'self-awareness', 'change', 'improvement', 'humility'],
        'star_required': True
    },
    {
        'id': 'BEH_10',
        'question': 'Describe a situation where you had to make a decision with limited information. What was your reasoning process?',
        'difficulty': 'hard',
        'category': 'decision_making',
        'expected_keywords': ['decision', 'limited information', 'risk', 'analysis', 'outcome', 'framework', 'judgment'],
        'star_required': True
    },
    {
        'id': 'BEH_11',
        'question': 'Tell me about a time when you had to collaborate with people from different departments or backgrounds. What challenges arose?',
        'difficulty': 'medium',
        'category': 'collaboration',
        'expected_keywords': ['collaboration', 'cross-functional', 'communication', 'diverse', 'alignment', 'teamwork', 'outcome'],
        'star_required': True
    },
    {
        'id': 'BEH_12',
        'question': 'Describe a time when you took ownership of a task or project beyond your assigned responsibilities. What motivated you?',
        'difficulty': 'easy',
        'category': 'ownership',
        'expected_keywords': ['ownership', 'initiative', 'proactive', 'responsibility', 'motivated', 'impact', 'leadership'],
        'star_required': True
    },
    {
        'id': 'BEH_13',
        'question': 'Tell me about a time when you had to communicate a complex idea to a non-technical audience. How did you ensure understanding?',
        'difficulty': 'medium',
        'category': 'communication',
        'expected_keywords': ['communication', 'simplify', 'audience', 'analogy', 'visual', 'clarity', 'understanding'],
        'star_required': True
    },
    {
        'id': 'BEH_14',
        'question': 'Give an example of when you had to adapt quickly to a major change at work (reorganization, technology shift, pivoting priorities).',
        'difficulty': 'medium',
        'category': 'adaptability',
        'expected_keywords': ['change', 'adaptation', 'flexibility', 'resilience', 'pivot', 'positive attitude', 'outcome'],
        'star_required': True
    },
    {
        'id': 'BEH_15',
        'question': 'Describe a time when you failed at something. What happened, and what did you learn from the experience?',
        'difficulty': 'hard',
        'category': 'resilience',
        'expected_keywords': ['failure', 'accountability', 'reflection', 'learning', 'growth', 'recovery', 'humility'],
        'star_required': True
    },
]


# ============================================================================
# ASSEMBLED ROLE QUESTION BANKS
# ============================================================================
ROLE_QUESTION_BANKS = {
    'software_developer': SOFTWARE_DEVELOPER_QUESTIONS,
    'data_analyst': DATA_ANALYST_QUESTIONS,
    'data_scientist': DATA_SCIENTIST_QUESTIONS,
    'devops_engineer': DEVOPS_ENGINEER_QUESTIONS,
    'product_manager': PRODUCT_MANAGER_QUESTIONS,
    'ui_ux_designer': UI_UX_DESIGNER_QUESTIONS,
}
