// Sample research papers database (simulating your vector search results)
const samplePapers = [
    {
        title: "Attention Is All You Need",
        abstract: "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train.",
        similarity: 0.94,
        keywords: ["Transformer", "Attention", "Neural Networks", "NLP", "Machine Translation"],
        authors: "Vaswani et al.",
        year: "2017",
        venue: "NIPS"
    },
    {
        title: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        abstract: "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text.",
        similarity: 0.91,
        keywords: ["BERT", "Transformers", "Pre-training", "Language Models", "Bidirectional"],
        authors: "Devlin et al.",
        year: "2019",
        venue: "NAACL"
    },
    {
        title: "Deep Residual Learning for Image Recognition",
        abstract: "We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously. We explicitly reformulate the layers as learning residual functions with reference to the layer inputs, instead of learning unreferenced functions.",
        similarity: 0.88,
        keywords: ["ResNet", "Computer Vision", "Deep Learning", "Image Recognition", "CNN"],
        authors: "He et al.",
        year: "2016",
        venue: "CVPR"
    },
    {
        title: "Generative Adversarial Networks",
        abstract: "We propose a new framework for estimating generative models via an adversarial process, in which we simultaneously train two models: a generative model G that captures the data distribution, and a discriminative model D that estimates the probability that a sample came from the training data rather than G.",
        similarity: 0.85,
        keywords: ["GANs", "Generative Models", "Adversarial Training", "Deep Learning", "Game Theory"],
        authors: "Goodfellow et al.",
        year: "2014",
        venue: "NIPS"
    },
    {
        title: "You Only Look Once: Unified, Real-Time Object Detection",
        abstract: "We present YOLO, a new approach to object detection. Prior work on object detection repurposes classifiers to perform detection. Instead, we frame object detection as a regression problem to spatially separated bounding boxes and associated class probabilities.",
        similarity: 0.82,
        keywords: ["YOLO", "Object Detection", "Computer Vision", "Real-time", "CNN"],
        authors: "Redmon et al.",
        year: "2016",
        venue: "CVPR"
    },
    {
        title: "Mastering the Game of Go with Deep Neural Networks and Tree Search",
        abstract: "The game of Go has long been viewed as the most challenging of classic games for artificial intelligence owing to its enormous search space and the difficulty of evaluating board positions and moves. Here we introduce a new approach to computer Go that uses 'value networks' to evaluate board positions and 'policy networks' to select moves.",
        similarity: 0.79,
        keywords: ["AlphaGo", "Reinforcement Learning", "Deep Learning", "Monte Carlo Tree Search", "Game AI"],
        authors: "Silver et al.",
        year: "2016",
        venue: "Nature"
    },
    {
        title: "ImageNet Classification with Deep Convolutional Neural Networks",
        abstract: "We trained a large, deep convolutional neural network to classify the 1.2 million high-resolution images in the ImageNet LSVRC-2010 contest into the 1000 different classes. On the test data, we achieved top-1 and top-5 error rates of 37.5% and 17.0% which is considerably better than the previous state-of-the-art.",
        similarity: 0.76,
        keywords: ["AlexNet", "CNN", "ImageNet", "Deep Learning", "Computer Vision"],
        authors: "Krizhevsky et al.",
        year: "2012",
        venue: "NIPS"
    },
    {
        title: "Neural Machine Translation by Jointly Learning to Align and Translate",
        abstract: "Neural machine translation is a recently proposed approach to machine translation. Unlike the traditional statistical machine translation, the neural machine translation aims at building a single neural network that can be jointly tuned to maximize the translation performance.",
        similarity: 0.73,
        keywords: ["Neural Machine Translation", "Attention Mechanism", "RNN", "Sequence-to-Sequence", "NLP"],
        authors: "Bahdanau et al.",
        year: "2015",
        venue: "ICLR"
    }
];

// Additional papers for different domains
const additionalPapers = [
    {
        title: "Explaining and Harnessing Adversarial Examples",
        abstract: "Several machine learning models, including neural networks, consistently misclassify adversarial examples---inputs formed by applying small but intentionally worst-case perturbations to examples from the dataset, such that the perturbed input results in the model outputting an incorrect answer with high confidence.",
        similarity: 0.89,
        keywords: ["Adversarial Examples", "Machine Learning Security", "Neural Networks", "Interpretability"],
        authors: "Goodfellow et al.",
        year: "2015",
        venue: "ICLR"
    },
    {
        title: "Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks",
        abstract: "We propose an algorithm for meta-learning that is model-agnostic, in the sense that it is compatible with any model trained with gradient descent and applicable to a variety of different learning problems, including classification, regression, and reinforcement learning.",
        similarity: 0.86,
        keywords: ["Meta-Learning", "Few-Shot Learning", "Model-Agnostic", "Deep Learning", "Adaptation"],
        authors: "Finn et al.",
        year: "2017",
        venue: "ICML"
    },
    {
        title: "Deep Reinforcement Learning with Double Q-Learning",
        abstract: "The popular Q-learning algorithm is known to overestimate action values under certain conditions. It was not previously known whether, in practice, such overestimations are common, whether this harms performance, and whether they can generally be prevented.",
        similarity: 0.84,
        keywords: ["Deep Q-Learning", "Reinforcement Learning", "Q-Networks", "Overestimation Bias"],
        authors: "van Hasselt et al.",
        year: "2016",
        venue: "AAAI"
    }
];

// Combine all papers
const allPapers = [...samplePapers, ...additionalPapers];

function searchQuery(query) {
    document.getElementById('searchInput').value = query;
    performSearch();
}

function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) {
        alert('Please enter a search query');
        return;
    }

    const resultsDiv = document.getElementById('searchResults');
    
    // Show loading
    resultsDiv.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>🔍 Searching through 50,000+ research papers...</p>
            <p>⚡ Computing vector similarities with sub-millisecond precision...</p>
            <p>🧠 Using semantic understanding to find relevant papers...</p>
        </div>
    `;

    // Simulate API call delay
    setTimeout(() => {
        displayResults(query);
        updateMetrics();
    }, 1500);
}

function displayResults(query) {
    const resultsDiv = document.getElementById('searchResults');
    
    // Filter and sort papers based on query (simulation)
    let relevantPapers = [...allPapers];
    
    // Simple keyword matching for demo (your actual implementation uses semantic similarity)
    const queryWords = query.toLowerCase().split(' ');
    relevantPapers = relevantPapers.map(paper => {
        let relevanceScore = 0;
        queryWords.forEach(word => {
            if (paper.title.toLowerCase().includes(word) || 
                paper.abstract.toLowerCase().includes(word) ||
                paper.keywords.some(k => k.toLowerCase().includes(word))) {
                relevanceScore += 0.1;
            }
        });
        return {
            ...paper,
            similarity: Math.min(0.98, paper.similarity + relevanceScore)
        };
    });

    // Sort by similarity score
    relevantPapers.sort((a,
