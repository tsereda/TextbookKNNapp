# Updated Knowledge Graph System Design Document

## 1. System Overview

This system integrates Vue.js for the frontend, Neo4j for graph database storage, Flask for the API backend, and a Python script for PDF processing and knowledge graph creation. The system aims to create a knowledge graph from PDF documents and provide an interactive interface for exploring the content. The API has been simplified to leverage direct Cypher queries where possible.

## 2. Components

### 2.1 Frontend (Vue.js)
- Displays the PDF document
- Visualizes the knowledge graph
- Displays questions for a selected chapter
- Shows similarity scores to different node types
- Presents top 5 relevant nodes
- Displays 3 most relevant PDF pages
- Dynamically lists chapters and problems
- Uses Cytoscape for graph visualization

### 2.2 Backend (Flask API)
- Handles requests from the frontend
- Executes Cypher queries directly on the Neo4j database
- Processes and returns data for frontend display
- Manages PDF storage and retrieval

### 2.3 Database (Neo4j)
- Stores the knowledge graph
- Nodes: Sections, Key Terms, Concepts, Media, Pages
- Relationships: Connections between nodes
- Stores page numbers for easy reference

### 2.4 PDF Processor (build_knowledge_graph.py)
- Processes PDF files added to the backend
- Creates nodes and relationships in the Neo4j database
- Precomputes the knowledge graph
- Associates page numbers with relevant nodes

## 3. Workflow

1. PDF Processing:
   - Admin adds PDFs to the backend
   - build_knowledge_graph.py processes the PDF
   - Extracts sections, key terms, concepts, media, and page numbers
   - Creates nodes and relationships in Neo4j
   - Precomputes the knowledge graph

2. User Interaction:
   - User views the PDF in the Vue.js frontend
   - User can explore the visualized knowledge graph
   - User selects a chapter or problem in the frontend
   - Frontend sends a request to the Flask API
   - API executes Cypher queries on Neo4j for relevant information
   - Frontend displays the results

3. Data Display:
   - PDF document
   - Interactive knowledge graph visualization
   - Dynamically listed chapters and problems
   - Questions for the selected chapter
   - Similarity scores to other node types
   - Top 5 relevant nodes (key terms, concepts, sections)
   - 3 most relevant PDF pages

## 4. API Endpoints and Cypher Queries

1. `/get_pdf_list`: GET request to retrieve the list of available PDFs (No Cypher query, requires backend processing)

2. `/get_pdf`: GET request to retrieve a specific PDF (No Cypher query, requires backend processing)

3. `/get_knowledge_graph`: GET request to retrieve the knowledge graph data
   Cypher query:
   ```cypher
   MATCH (n)
   OPTIONAL MATCH (n)-[r]->(m)
   RETURN n, r, m
   ```

4. `/get_chapters_and_problems`: GET request to get the list of chapters and problems
   Cypher query:
   ```cypher
   MATCH (c:Chapter), (p:Problem)
   RETURN c.title, collect(p.title)
   ```

5. `/get_chapter_questions`: GET request to retrieve questions for a chapter
   Cypher query:
   ```cypher
   MATCH (c:Chapter {title: $chapterTitle})-[:HAS_QUESTION]->(q:Question)
   RETURN q.text
   ```

6. `/get_similarity_scores`: GET request to get similarity scores for a node
   Partial Cypher query (may require additional processing):
   ```cypher
   MATCH (n {id: $nodeId})-[r:SIMILAR_TO]->(m)
   RETURN m.type, r.score
   ```

7. `/get_relevant_nodes`: GET request to retrieve top 5 relevant nodes
   Cypher query:
   ```cypher
   MATCH (n {id: $nodeId})-[r:RELATED_TO]->(m)
   RETURN m
   ORDER BY r.relevance DESC
   LIMIT 5
   ```

8. `/get_relevant_pages`: GET request to get 3 most relevant PDF pages
   Cypher query:
   ```cypher
   MATCH (n {id: $nodeId})-[:APPEARS_ON]->(p:Page)
   RETURN p
   ORDER BY p.relevance DESC
   LIMIT 3
   ```

## 5. Implementation Plan

1. Set up the development environment
   - Install necessary tools and frameworks (Vue.js, Flask, Neo4j, Python libraries)

2. Implement the PDF processor (build_knowledge_graph.py)
   - Develop PDF parsing and information extraction
   - Implement knowledge graph creation logic
   - Add page number association with nodes

3. Create the Neo4j database schema
   - Define node types (Sections, Key Terms, Concepts, Media, Pages)
   - Define relationship types
   - Set up appropriate indexes for optimized query performance

4. Develop the Flask API
   - Implement endpoints using direct Cypher queries where possible
   - Set up PDF storage and retrieval system
   - Implement a Neo4j driver for executing Cypher queries

5. Build the Vue.js frontend
   - Create PDF viewer component
   - Develop knowledge graph visualization component using Cytoscape
   - Implement chapter and problem listing
   - Design and implement the user interface for displaying relevant information

6. Integrate all components
   - Connect frontend with API
   - Ensure smooth data flow between all parts of the system

7. Test the system
   - Develop comprehensive test cases
   - Perform unit testing and integration testing
   - Test Cypher query performance and optimize as necessary

8. Optimize and refine
   - Improve performance of knowledge graph creation and querying
   - Enhance user interface based on testing feedback

## 6. Timeline and Milestones

- Week 1-2: Environment setup and PDF processor implementation
- Week 3-4: Neo4j schema creation and Flask API development with Cypher queries
- Week 5-6: Vue.js frontend development
- Week 7-8: Integration, testing, and optimization

## 7. Recommended Next Steps

1. Backend PDF Management:
   - Implement a dedicated storage solution for PDFs (e.g., file system directory, object storage service)
   - Develop an admin-level interface for adding and managing PDFs

2. PDF Indexing:
   - Create a simple indexing system for easier management and retrieval of multiple documents

3. Batch Processing:
   - Implement a feature to handle multiple PDFs at once for knowledge graph generation

4. PDF Metadata:
   - Extract and store metadata from PDFs (e.g., title, author, publication date) to enhance the knowledge graph

5. Version Control:
   - Implement a basic version control system for PDFs and their corresponding knowledge graphs

6. Error Handling and Logging:
   - Develop robust error handling and logging for PDF processing and knowledge graph generation

7. Performance Optimization:
   - Implement strategies for efficiently handling large PDFs or a large number of PDFs
   - Monitor and optimize Cypher query performance

8. User Authentication:
   - Add user authentication and authorization for accessing different parts of the system

9. Advanced Search and Filtering:
   - Develop advanced search and filtering capabilities within the knowledge graph using complex Cypher queries

10. Machine Learning Integration:
    - Integrate machine learning models for improved relevance scoring and recommendations

11. Cypher Query Optimization:
    - Regularly review and optimize Cypher queries for better performance as the graph grows
    - Implement query caching where appropriate

12. Neo4j to Frontend Data Transfer Optimization:
    - Implement efficient data serialization and transfer methods for large graph datasets

This updated design leverages direct Cypher queries to simplify the API and potentially improve performance. The backend now acts more as a thin layer between the frontend and the Neo4j database, primarily executing Cypher queries and handling PDF-related operations.