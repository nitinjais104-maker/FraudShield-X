const form = document.getElementById("fraudForm");
const resultContent = document.getElementById("resultContent");
const analyzeBtn = document.getElementById("analyzeBtn");

const amountInput = document.getElementById("amount");
const timeInput = document.getElementById("time");
const signalsInput = document.getElementById("signals");

const API_URL = "https://fraudshield-x.onrender.com/predict";
const MODEL_INFO_URL = "https://fraudshield-x.onrender.com/model-info";


/* =========================================================
   VERIFIED DEMO TRANSACTIONS
   Real examples from creditcard.csv
   ========================================================= */

const DEMO_TRANSACTIONS = {

    genuine: {
        amount: 799.14,
        time: 147647,

        signals: [
            -8.380983, -7.984275, -2.103946, -0.297072,
            -1.825192, 2.098350, 2.830241, 0.119530,
            -0.631697, -0.652259, 0.813084, -0.046783,
            0.276146, -0.241820, -0.113394, 1.697527,
            0.407664, -2.311113, 0.044021, -1.706724,
            -0.823561, -0.542000, 0.839478, -1.499438,
            0.691734, -0.460079, -0.634305, 0.700637
        ]
    },


    review: {
        amount: 278.56,
        time: 152474,

        signals: [
            -0.802178, -0.460159, -0.335956, -0.396395,
            0.869876, -0.495807, 1.665550, -0.311734,
            0.303737, -1.674422, -0.620191, -0.294898,
            -0.237979, -1.893108, -0.334560, 0.037014,
            0.969257, 0.288406, -0.171383, 0.717147,
            -0.082297, -0.571063, 0.528454, 0.431905,
            0.326206, -0.141887, -0.288424, -0.180716
        ]
    },


    fraud: {
        amount: 153.46,
        time: 56624,

        signals: [
            -7.901421, 2.720472, -7.885936, 6.348334,
            -5.480119, -0.333059, -8.682376, 1.164431,
            -4.542447, -7.748480, 5.266586, -8.679679,
            -1.166366, -8.107975, 0.701365, -6.288306,
            -13.753131, -4.329239, 1.504250, -0.614719,
            0.077739, 1.092437, 0.320133, -0.434643,
            -0.380687, 0.213630, 0.423620, -0.105169
        ]
    }
};


/* =========================================================
   MODEL INFORMATION
   ========================================================= */

async function loadModelInfo() {

    try {

        const response = await fetch(MODEL_INFO_URL);

        if (!response.ok) {
            throw new Error("Model information unavailable");
        }

        const data = await response.json();

        document.querySelectorAll("[data-model]").forEach(el => {
            el.textContent = data.model;
        });

        document.querySelectorAll("[data-features]").forEach(el => {
            el.textContent = data.features;
        });

        document.querySelectorAll("[data-threshold]").forEach(el => {
            el.textContent = Number(data.threshold).toFixed(2);
        });

        document.querySelectorAll("[data-pr-auc]").forEach(el => {
            el.textContent = Number(data.pr_auc).toFixed(3);
        });

        document.querySelectorAll("[data-precision]").forEach(el => {
            el.textContent =
                (Number(data.precision) * 100).toFixed(2) + "%";
        });

        document.querySelectorAll("[data-recall]").forEach(el => {
            el.textContent =
                (Number(data.recall) * 100).toFixed(2) + "%";
        });

        document.querySelectorAll("[data-f1]").forEach(el => {
            el.textContent =
                (Number(data.f1_score) * 100).toFixed(2) + "%";
        });

        console.log("FraudShield X Model:", data);

    } catch (error) {

        console.error("Model info error:", error);
    }
}


/* =========================================================
   ERROR DISPLAY
   ========================================================= */

function showError(title, message) {

    resultContent.innerHTML = `
        <div class="result-placeholder">

            <div class="result-icon">!</div>

            <h3>${title}</h3>

            <p>${message}</p>

        </div>
    `;
}


/* =========================================================
   LOAD DEMO TRANSACTION
   ========================================================= */

function loadDemoTransaction(type) {

    const transaction = DEMO_TRANSACTIONS[type];

    if (!transaction) {
        return;
    }

    amountInput.value = transaction.amount;
    timeInput.value = transaction.time;

    signalsInput.value =
        transaction.signals.join(",");

    const labels = {
        genuine: "GENUINE",
        review: "REVIEW",
        fraud: "HIGH-RISK FRAUD"
    };

    resultContent.innerHTML = `
        <div class="result-placeholder">

            <div class="result-icon">✓</div>

            <h3>${labels[type]} DEMO LOADED</h3>

            <p>
                A verified dataset transaction has been loaded.
                Click <strong>Analyze Transaction</strong>
                to run the Random Forest model.
            </p>

        </div>
    `;
}


/* =========================================================
   FORM SUBMISSION
   ========================================================= */

form.addEventListener("submit", async (event) => {

    event.preventDefault();

    const amount = Number(amountInput.value);
    const time = Number(timeInput.value);
    const rawSignals = signalsInput.value.trim();


    /* -----------------------------
       VALIDATION
    ----------------------------- */

    if (
        !amountInput.value ||
        Number.isNaN(amount) ||
        amount < 0
    ) {

        showError(
            "Invalid Amount",
            "Please enter a valid transaction amount."
        );

        return;
    }


    if (
        !timeInput.value ||
        Number.isNaN(time) ||
        time < 0
    ) {

        showError(
            "Invalid Transaction Time",
            "Please enter a valid transaction time."
        );

        return;
    }


    if (!rawSignals) {

        showError(
            "Missing Transaction Signals",
            "Please enter the V1–V28 transaction signals."
        );

        return;
    }


    const signals = rawSignals
        .split(",")
        .map(value => Number(value.trim()));


    if (signals.length !== 28) {

        showError(
            "Invalid Signal Count",
            `The model requires exactly 28 signals.
             You entered ${signals.length}.`
        );

        return;
    }


    if (signals.some(value => Number.isNaN(value))) {

        showError(
            "Invalid Signal",
            "All V1–V28 values must be valid numbers."
        );

        return;
    }


    /* -----------------------------
       API PAYLOAD
       ----------------------------- */

    const payload = {
        Time: time,
        Amount: amount
    };


    signals.forEach((value, index) => {

        payload[`V${index + 1}`] = value;

    });


    console.log("Prediction payload:", payload);


    /* -----------------------------
       LOADING STATE
       ----------------------------- */

    analyzeBtn.disabled = true;

    analyzeBtn.innerHTML = `
        <span>Analyzing...</span>
        <span>...</span>
    `;


    resultContent.innerHTML = `
        <div class="result-placeholder">

            <div class="result-icon">AI</div>

            <h3>Analyzing Transaction</h3>

            <p>
                FraudShield X is processing the transaction
                through the Random Forest detection engine.
            </p>

        </div>
    `;


    /* -----------------------------
       API REQUEST
       ----------------------------- */

    try {

        const response = await fetch(
            API_URL,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(payload)
            }
        );


        const data = await response.json();


        if (!response.ok || data.error) {

            throw new Error(
                data.error || "Prediction request failed."
            );
        }


        const probability =
            Number(data.fraud_probability) * 100;

        const probabilityText =
            probability.toFixed(2);


        /* =================================================
           HIGH RISK
           ================================================= */

        if (data.prediction === 1) {

            resultContent.innerHTML = `

                <div class="result-fraud">

                    <div class="result-icon">!</div>

                    <div class="risk-title">
                        HIGH RISK
                    </div>

                    <div class="risk-subtitle">
                        Potential fraudulent transaction detected
                    </div>

                    <div class="probability">

                        <div class="probability-value">
                            ${probabilityText}%
                        </div>

                        <span class="probability-label">
                            Fraud Probability
                        </span>

                    </div>

                    <div class="risk-bar">

                        <div
                            class="risk-fill"
                            style="
                                width:${probabilityText}%;
                                background:#ef4444;
                            "
                        ></div>

                    </div>

                    <div class="decision-label">
                        Decision: FRAUD
                    </div>

                </div>
            `;

        }


        /* =================================================
           REVIEW
           ================================================= */

        else if (probability >= 30) {

            resultContent.innerHTML = `

                <div class="result-review">

                    <div class="result-icon">!</div>

                    <div class="risk-title">
                        REVIEW REQUIRED
                    </div>

                    <div class="risk-subtitle">
                        Transaction requires additional review
                    </div>

                    <div class="probability">

                        <div class="probability-value">
                            ${probabilityText}%
                        </div>

                        <span class="probability-label">
                            Fraud Probability
                        </span>

                    </div>

                    <div class="risk-bar">

                        <div
                            class="risk-fill"
                            style="
                                width:${probabilityText}%;
                                background:#f59e0b;
                            "
                        ></div>

                    </div>

                    <div class="decision-label">
                        Decision: MANUAL REVIEW
                    </div>

                </div>
            `;

        }


        /* =================================================
           LOW RISK
           ================================================= */

        else {

            resultContent.innerHTML = `

                <div class="result-genuine">

                    <div class="result-icon">✓</div>

                    <div class="risk-title">
                        LOW RISK
                    </div>

                    <div class="risk-subtitle">
                        Transaction appears to be genuine
                    </div>

                    <div class="probability">

                        <div class="probability-value">
                            ${probabilityText}%
                        </div>

                        <span class="probability-label">
                            Fraud Probability
                        </span>

                    </div>

                    <div class="risk-bar">

                        <div
                            class="risk-fill"
                            style="
                                width:${probabilityText}%;
                                background:#22c55e;
                            "
                        ></div>

                    </div>

                    <div class="decision-label">
                        Decision: GENUINE
                    </div>

                </div>
            `;
        }


    } catch (error) {

        console.error("Prediction error:", error);

        resultContent.innerHTML = `

            <div class="result-placeholder">

                <div class="result-icon">X</div>

                <h3>Connection Error</h3>

                <p>
                    Unable to connect to the FraudShield X API.
                    Make sure the FastAPI server is running.
                </p>

            </div>
        `;

    } finally {

        analyzeBtn.disabled = false;

        analyzeBtn.innerHTML = `
            <span>Analyze Transaction</span>
            <span>→</span>
        `;
    }

});


/* =========================================================
   DEMO BUTTON EVENTS
   ========================================================= */

const demoGenuine =
    document.getElementById("demoGenuine");

const demoReview =
    document.getElementById("demoReview");

const demoFraud =
    document.getElementById("demoFraud");


if (demoGenuine) {

    demoGenuine.addEventListener(
        "click",
        () => loadDemoTransaction("genuine")
    );
}


if (demoReview) {

    demoReview.addEventListener(
        "click",
        () => loadDemoTransaction("review")
    );
}


if (demoFraud) {

    demoFraud.addEventListener(
        "click",
        () => loadDemoTransaction("fraud")
    );
}


/* =========================================================
   INITIALIZE
   ========================================================= */

loadModelInfo();