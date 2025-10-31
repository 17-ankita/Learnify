// ✅ Import dependencies
import express from "express";
import fs from "fs";
import cors from "cors";

const app = express();
app.use(cors());
app.use(express.json());

// ✅ TEST ROUTE — check server
app.get("/", (req, res) => {
  res.send("✅ Backend is running fine!");
});

// ✅ POST route to save quiz data to CSV
app.post("/save-quiz", (req, res) => {
  const data = req.body;

  if (!data || !Array.isArray(data)) {
    return res.status(400).json({ message: "Invalid data format. Expected an array." });
  }

  const csvHeader = "question,optionA,optionB,optionC,optionD,correctAnswer\n";
  const csvRows = data
    .map(
      (item) =>
        `"${item.question}","${item.optionA}","${item.optionB}","${item.optionC}","${item.optionD}","${item.correctAnswer}"`
    )
    .join("\n");

  const filePath = "quiz_data.csv";

  // Write or append the file
  if (!fs.existsSync(filePath)) {
    fs.writeFileSync(filePath, csvHeader + csvRows + "\n");
  } else {
    fs.appendFileSync(filePath, csvRows + "\n");
  }

  res.json({ message: "✅ Data saved successfully to quiz_data.csv" });
});

// ✅ Start server
const PORT = 5000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
