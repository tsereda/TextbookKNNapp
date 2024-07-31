<script>
import { onMount } from 'svelte';
import PDFViewer from './components/PDFViewer.svelte';
import KnowledgeGraph from './components/KnowledgeGraph.svelte';

let pdfFile;
let knowledgeGraphData = { nodes: [], edges: [] };

async function handleFileUpload(event) {
    const file = event.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('http://localhost:8000/upload-pdf', {
        method: 'POST',
        body: formData
    });
    
    if (response.ok) {
        fetchKnowledgeGraph();
    }
}

async function fetchKnowledgeGraph() {
    const response = await fetch('http://localhost:8000/knowledge-graph');
    knowledgeGraphData = await response.json();
}

onMount(fetchKnowledgeGraph);
</script>

<main>
    <h1>TEXTBOOKKN</h1>
    <input type="file" accept=".pdf" on:change={handleFileUpload}>
    <div class="container">
        <PDFViewer {pdfFile} />
        <KnowledgeGraph data={knowledgeGraphData} />
    </div>
</main>

<style>
    .container {
        display: flex;
        justify-content: space-between;
    }
</style>
