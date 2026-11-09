/**
 * SR University Academic Performance Analysis Portal
 * Client-Side Controller, Chart Renderer, and Multi-Step Engine
 */

let currentStep = 1;
const totalSteps = 5;
let currentStudentId = null;

// Chart instances
let gpaChartInstance = null;
let radarChartInstance = null;
let subjectChartInstance = null;
let deptChartInstance = null;
let riskDonutInstance = null;

// Department Preset Curriculums
const DEPARTMENT_CURRICULA = {
  "Computer Science & Engineering": [
    { code: "CS301", name: "Design & Analysis of Algorithms", credits: 4, internal: 44, max: 50, att: 92, grade: "A+" },
    { code: "CS302", name: "Database Management Systems", credits: 4, internal: 41, max: 50, att: 88, grade: "A" },
    { code: "CS303", name: "Operating Systems Architecture", credits: 4, internal: 38, max: 50, att: 84, grade: "B+" },
    { code: "CS304", name: "Computer Networks & Protocols", credits: 3, internal: 45, max: 50, att: 90, grade: "A+" },
    { code: "CS305", name: "Algorithms & Systems Lab", credits: 2, internal: 48, max: 50, att: 95, grade: "O" }
  ],
  "Artificial Intelligence & Data Science": [
    { code: "AI201", name: "Deep Learning Foundations", credits: 4, internal: 38, max: 50, att: 86, grade: "A" },
    { code: "AI202", name: "Probability & Applied Statistics", credits: 4, internal: 35, max: 50, att: 80, grade: "B+" },
    { code: "AI203", name: "Big Data Systems & Hadoop", credits: 4, internal: 42, max: 50, att: 89, grade: "A" },
    { code: "AI204", name: "Computer Vision Fundamentals", credits: 3, internal: 40, max: 50, att: 82, grade: "A" },
    { code: "AI205", name: "AI & Neural Networks Lab", credits: 2, internal: 46, max: 50, att: 94, grade: "O" }
  ],
  "Electronics & Communication": [
    { code: "EC301", name: "Digital Signal Processing", credits: 4, internal: 36, max: 50, att: 82, grade: "B+" },
    { code: "EC302", name: "VLSI Circuit Design", credits: 4, internal: 40, max: 50, att: 86, grade: "A" },
    { code: "EC303", name: "Electromagnetic Waves & Antennas", credits: 4, internal: 34, max: 50, att: 78, grade: "B" },
    { code: "EC304", name: "Microcontrollers & Embedded Systems", credits: 3, internal: 43, max: 50, att: 90, grade: "A+" },
    { code: "EC305", name: "VLSI & Embedded Lab", credits: 2, internal: 45, max: 50, att: 92, grade: "O" }
  ],
  "Mechanical Engineering": [
    { code: "ME301", name: "Applied Thermodynamics", credits: 4, internal: 37, max: 50, att: 84, grade: "B+" },
    { code: "ME302", name: "Fluid Mechanics & Turbo Machinery", credits: 4, internal: 35, max: 50, att: 80, grade: "B" },
    { code: "ME303", name: "Kinematics of Machinery", credits: 4, internal: 41, max: 50, att: 88, grade: "A" },
    { code: "ME304", name: "Heat Transfer Operations", credits: 3, internal: 39, max: 50, att: 85, grade: "A" },
    { code: "ME305", name: "CAD/CAM Simulation Lab", credits: 2, internal: 46, max: 50, att: 92, grade: "O" }
  ],
  "Management Studies (MBA)": [
    { code: "MBA101", name: "Strategic Financial Management", credits: 4, internal: 42, max: 50, att: 89, grade: "A" },
    { code: "MBA102", name: "Marketing Analytics & Strategy", credits: 4, internal: 44, max: 50, att: 92, grade: "A+" },
    { code: "MBA103", name: "Operations & Supply Chain", credits: 4, internal: 39, max: 50, att: 85, grade: "B+" },
    { code: "MBA104", name: "Organizational Leadership", credits: 3, internal: 46, max: 50, att: 94, grade: "A+" },
    { code: "MBA105", name: "Business Case Studies Practicum", credits: 2, internal: 48, max: 50, att: 96, grade: "O" }
  ]
};

// Initialization on DOM Loaded
document.addEventListener("DOMContentLoaded", () => {
  generateSemesterInputs();
  loadDefaultCurriculum();
  setupAttendanceListener();

  // Load initial demo view in dashboard if exists
  fetchLatestOrFirstStudent();
});

// Toast Notifications
function showToast(message, isSuccess = true) {
  const toast = document.getElementById("toast");
  const msgEl = document.getElementById("toast-msg");
  const iconEl = document.getElementById("toast-icon");

  msgEl.textContent = message;
  iconEl.className = isSuccess 
    ? "fa-solid fa-circle-check text-emerald-400 text-lg" 
    : "fa-solid fa-circle-exclamation text-rose-400 text-lg";

  toast.classList.remove("hidden");
  setTimeout(() => {
    toast.classList.add("hidden");
  }, 4000);
}

// Tab Switching
function switchTab(tabId) {
  const tabs = ["form", "dashboard", "faculty"];
  tabs.forEach(t => {
    const section = document.getElementById(`${t}-tab`);
    const btn = document.getElementById(`nav-${t}-btn`);
    if (t === tabId) {
      section.classList.remove("hidden");
      btn.className = "nav-tab px-3.5 py-2 text-sm font-medium rounded-lg text-brand-700 bg-brand-50 border border-brand-200 transition-all flex items-center space-x-2";
    } else {
      section.classList.add("hidden");
      btn.className = "nav-tab px-3.5 py-2 text-sm font-medium rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-all flex items-center space-x-2";
    }
  });

  if (tabId === "faculty") {
    loadCohortAnalytics();
    loadStudentDirectory();
  }
}

// Multi-step Wizard Navigation
function goToStep(step) {
  if (step < 1 || step > totalSteps) return;

  // Validate step 1 if advancing
  if (step > 1 && currentStep === 1) {
    const fullName = document.getElementById("fullName").value.trim();
    const rollNo = document.getElementById("rollNo").value.trim();
    const email = document.getElementById("email").value.trim();
    if (!fullName || !rollNo || !email) {
      showToast("Please fill in Name, Roll Number, and Email.", false);
      return;
    }
  }

  // Update Summary on Step 5
  if (step === 5) {
    populateReviewSummary();
  }

  currentStep = step;

  // Update step visibility
  for (let i = 1; i <= totalSteps; i++) {
    const content = document.getElementById(`form-step-${i}`);
    const badge = document.getElementById(`step-badge-${i}`);
    if (i === currentStep) {
      content.classList.remove("hidden");
      badge.className = "w-10 h-10 rounded-full bg-brand-600 text-white flex items-center justify-center font-bold text-sm shadow-md transition-all step-active";
    } else if (i < currentStep) {
      content.classList.add("hidden");
      badge.className = "w-10 h-10 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold text-sm transition-all step-completed";
      badge.innerHTML = '<i class="fa-solid fa-check text-xs"></i>';
    } else {
      content.classList.add("hidden");
      badge.className = "w-10 h-10 rounded-full bg-white text-slate-500 border-2 border-slate-300 flex items-center justify-center font-bold text-sm transition-all";
      badge.textContent = i;
    }
  }

  // Update progress bar width
  const progressPercent = ((currentStep - 1) / (totalSteps - 1)) * 100;
  document.getElementById("step-progress-bar").style.width = `${progressPercent}%`;

  // Buttons
  document.getElementById("prev-btn").classList.toggle("hidden", currentStep === 1);
  if (currentStep === totalSteps) {
    document.getElementById("next-btn").classList.add("hidden");
    document.getElementById("submit-btn").classList.remove("hidden");
  } else {
    document.getElementById("next-btn").classList.remove("hidden");
    document.getElementById("submit-btn").classList.add("hidden");
  }
}

function nextStep() {
  goToStep(currentStep + 1);
}

function prevStep() {
  goToStep(currentStep - 1);
}

// Attendance input warning
function setupAttendanceListener() {
  const attInput = document.getElementById("overallAttendance");
  const warnEl = document.getElementById("attendance-warning");

  attInput.addEventListener("input", () => {
    const val = parseFloat(attInput.value) || 0;
    if (val < 75.0) {
      warnEl.className = "text-[11px] text-rose-600 font-semibold block mt-1";
      warnEl.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Below 75% Cutoff: Debarment / Condonation Risk!';
    } else if (val < 80.0) {
      warnEl.className = "text-[11px] text-amber-600 font-medium block mt-1";
      warnEl.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i> Warning Band: Borderline attendance (75-80%)';
    } else {
      warnEl.className = "text-[11px] text-emerald-600 font-medium block mt-1";
      warnEl.innerHTML = '<i class="fa-solid fa-circle-check"></i> Eligible for End-Semester Examinations (>= 75%)';
    }
  });
}

// Dynamic Semester Row Generation
function generateSemesterInputs() {
  const currentSem = parseInt(document.getElementById("currentSemester").value) || 1;
  const container = document.getElementById("semester-rows-container");
  container.innerHTML = "";

  if (currentSem === 1) {
    container.innerHTML = `
      <tr>
        <td colspan="5" class="py-4 px-4 text-center text-xs text-slate-500 italic bg-slate-50/50">
          First semester student. Cumulative CGPA will be calculated from current semester internal assessments.
        </td>
      </tr>
    `;
    updateLiveCGPA();
    return;
  }

  for (let sem = 1; sem < currentSem; sem++) {
    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-50/70 transition-colors";
    tr.innerHTML = `
      <td class="py-2.5 px-4 font-semibold text-slate-800">Semester ${sem}</td>
      <td class="py-2.5 px-4">
        <input type="number" min="0" max="10" step="0.01" value="8.00" 
               class="sem-sgpa-input w-28 px-3 py-1.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-xs font-semibold"
               data-sem="${sem}" oninput="updateLiveCGPA()">
      </td>
      <td class="py-2.5 px-4">
        <input type="number" min="1" max="40" value="23" 
               class="sem-reg-input w-24 px-3 py-1.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-xs"
               data-sem="${sem}" oninput="updateLiveCGPA()">
      </td>
      <td class="py-2.5 px-4">
        <input type="number" min="0" max="40" value="23" 
               class="sem-cleared-input w-24 px-3 py-1.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-xs"
               data-sem="${sem}">
      </td>
      <td class="py-2.5 px-4">
        <input type="number" min="0" max="10" value="0" 
               class="sem-backlogs-input w-20 px-3 py-1.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-xs"
               data-sem="${sem}">
      </td>
    `;
    container.appendChild(tr);
  }

  updateLiveCGPA();
}

// Live CGPA Calculation
function updateLiveCGPA() {
  const sgpaInputs = document.querySelectorAll(".sem-sgpa-input");
  const regInputs = document.querySelectorAll(".sem-reg-input");

  if (sgpaInputs.length === 0) {
    document.getElementById("live-cgpa-display").textContent = "N/A (Sem 1)";
    return;
  }

  let totalPoints = 0;
  let totalCredits = 0;

  sgpaInputs.forEach((input, idx) => {
    const sgpa = parseFloat(input.value) || 0;
    const credits = parseFloat(regInputs[idx]?.value) || 20;
    totalPoints += (sgpa * credits);
    totalCredits += credits;
  });

  const cgpa = totalCredits > 0 ? (totalPoints / totalCredits).toFixed(2) : "0.00";
  document.getElementById("live-cgpa-display").textContent = cgpa;
}

// Department change handler
function onDepartmentChange() {
  loadDefaultCurriculum();
}

// Load Default Curriculum Subjects
function loadDefaultCurriculum() {
  const dept = document.getElementById("department").value;
  const list = DEPARTMENT_CURRICULA[dept] || DEPARTMENT_CURRICULA["Computer Science & Engineering"];
  const container = document.getElementById("subject-rows-container");
  container.innerHTML = "";

  list.forEach(subj => {
    addSubjectRow(subj.code, subj.name, subj.credits, subj.internal, subj.max, subj.att, subj.grade);
  });
}

// Add Subject Row
function addSubjectRow(code = "", name = "", credits = 3, internal = 35, max = 50, att = 85, grade = "A") {
  const container = document.getElementById("subject-rows-container");
  const tr = document.createElement("tr");
  tr.className = "hover:bg-slate-50/70 transition-colors";
  tr.innerHTML = `
    <td class="py-2 px-3">
      <input type="text" placeholder="CS301" value="${code}" 
             class="subj-code w-full px-2.5 py-1.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-xs font-mono uppercase">
    </td>
    <td class="py-2 px-3">
      <input type="text" placeholder="Subject Name" value="${name}" 
             class="subj-name w-full px-2.5 py-1.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-xs">
    </td>
    <td class="py-2 px-3">
      <input type="number" min="1" max="10" value="${credits}" 
             class="subj-credits w-full px-2 py-1.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-xs">
    </td>
    <td class="py-2 px-3">
      <input type="number" min="0" max="50" step="0.5" value="${internal}" 
             class="subj-internal w-full px-2 py-1.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-xs font-semibold">
    </td>
    <td class="py-2 px-3">
      <div class="relative">
        <input type="number" min="0" max="100" step="1" value="${att}" 
               class="subj-att w-full px-2 py-1.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-xs font-semibold ${att < 75 ? 'border-rose-400 bg-rose-50 text-rose-700' : ''}">
      </div>
    </td>
    <td class="py-2 px-3">
      <select class="subj-grade w-full px-2 py-1.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-xs bg-white">
        <option value="A+" ${grade === 'A+' ? 'selected' : ''}>A+ (Outstanding)</option>
        <option value="A" ${grade === 'A' ? 'selected' : ''}>A (Excellent)</option>
        <option value="B+" ${grade === 'B+' ? 'selected' : ''}>B+ (Very Good)</option>
        <option value="B" ${grade === 'B' ? 'selected' : ''}>B (Good)</option>
        <option value="C" ${grade === 'C' ? 'selected' : ''}>C (Fair)</option>
        <option value="D" ${grade === 'D' ? 'selected' : ''}>D (Pass)</option>
        <option value="F" ${grade === 'F' ? 'selected' : ''}>F (Fail)</option>
      </select>
    </td>
    <td class="py-2 px-3 text-center">
      <button type="button" onclick="this.closest('tr').remove()" 
              class="w-7 h-7 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition flex items-center justify-center">
        <i class="fa-regular fa-trash-can text-xs"></i>
      </button>
    </td>
  `;
  container.appendChild(tr);
}

// Autofill Demo Data
function autofillDemo(type) {
  if (type === "high_performer") {
    document.getElementById("fullName").value = "Aarav Sharma";
    document.getElementById("rollNo").value = "21CS042";
    document.getElementById("email").value = "aarav.sharma@sruniv.edu";
    document.getElementById("department").value = "Computer Science & Engineering";
    document.getElementById("degreeProgram").value = "B.Tech";
    document.getElementById("currentSemester").value = "6";
    document.getElementById("academicYear").value = "2023-2027";
    document.getElementById("mentorName").value = "Dr. R. Ramanujan";
    document.getElementById("overallAttendance").value = "91.5";
    document.getElementById("activeBacklogs").value = "0";
    document.getElementById("weeklyStudyHours").value = "15-20 hours";
    document.getElementById("sleepHours").value = "7 hours";
    document.getElementById("stressLevel").value = "Moderate";
    document.getElementById("careerGoal").value = "Campus Placements / Software Engineer";

    generateSemesterInputs();
    const sgpaVals = [8.40, 8.65, 8.80, 8.90, 8.95];
    document.querySelectorAll(".sem-sgpa-input").forEach((inp, idx) => {
      if (sgpaVals[idx]) inp.value = sgpaVals[idx];
    });

    loadDefaultCurriculum();
    showToast("Filled demo data: Aarav Sharma (High Performer)");
  } else if (type === "at_risk") {
    document.getElementById("fullName").value = "Priya Nair";
    document.getElementById("rollNo").value = "22AI018";
    document.getElementById("email").value = "priya.nair@sruniv.edu";
    document.getElementById("department").value = "Artificial Intelligence & Data Science";
    document.getElementById("degreeProgram").value = "B.Tech";
    document.getElementById("currentSemester").value = "4";
    document.getElementById("academicYear").value = "2024-2028";
    document.getElementById("mentorName").value = "Prof. Ananya Sen";
    document.getElementById("overallAttendance").value = "68.0";
    document.getElementById("activeBacklogs").value = "2";
    document.getElementById("weeklyStudyHours").value = "< 5 hours";
    document.getElementById("sleepHours").value = "< 5 hours";
    document.getElementById("stressLevel").value = "High";
    document.getElementById("careerGoal").value = "Campus Placements / Software Engineer";

    generateSemesterInputs();
    const sgpaVals = [7.10, 6.20, 5.75];
    document.querySelectorAll(".sem-sgpa-input").forEach((inp, idx) => {
      if (sgpaVals[idx]) inp.value = sgpaVals[idx];
    });

    loadDefaultCurriculum();
    // Lower some marks for at-risk profile
    const rows = document.querySelectorAll("#subject-rows-container tr");
    if (rows.length >= 2) {
      rows[0].querySelector(".subj-internal").value = 21;
      rows[0].querySelector(".subj-att").value = 62;
      rows[1].querySelector(".subj-internal").value = 24;
      rows[1].querySelector(".subj-att").value = 65;
    }

    showToast("Filled demo data: Priya Nair (At-Risk Profile)");
  } else {
    document.getElementById("fullName").value = "Rohan Deshmukh";
    document.getElementById("rollNo").value = "23EC077";
    document.getElementById("email").value = "rohan.deshmukh@sruniv.edu";
    document.getElementById("department").value = "Electronics & Communication";
    document.getElementById("degreeProgram").value = "B.Tech";
    document.getElementById("currentSemester").value = "4";
    document.getElementById("academicYear").value = "2024-2028";
    document.getElementById("mentorName").value = "Dr. V. K. Murthy";
    document.getElementById("overallAttendance").value = "82.0";
    document.getElementById("activeBacklogs").value = "0";
    document.getElementById("weeklyStudyHours").value = "10-15 hours";
    document.getElementById("sleepHours").value = "6 hours";
    document.getElementById("stressLevel").value = "Moderate";
    document.getElementById("careerGoal").value = "Core Engineering / R&D";

    generateSemesterInputs();
    const sgpaVals = [7.50, 7.65, 7.80];
    document.querySelectorAll(".sem-sgpa-input").forEach((inp, idx) => {
      if (sgpaVals[idx]) inp.value = sgpaVals[idx];
    });

    loadDefaultCurriculum();
    showToast("Filled demo data: Rohan Deshmukh (Steady Performer)");
  }

  updateLiveCGPA();
  setupAttendanceListener();
}

// Populate Step 5 Summary
function populateReviewSummary() {
  document.getElementById("rev-name").textContent = document.getElementById("fullName").value || "--";
  document.getElementById("rev-roll").textContent = document.getElementById("rollNo").value || "--";
  document.getElementById("rev-dept").textContent = `${document.getElementById("department").value} (${document.getElementById("degreeProgram").value})`;
  document.getElementById("rev-sem").textContent = `Semester ${document.getElementById("currentSemester").value}`;
  document.getElementById("rev-cgpa").textContent = document.getElementById("live-cgpa-display").textContent;
  document.getElementById("rev-attendance").textContent = `${document.getElementById("overallAttendance").value}%`;
}

// Submit Academic Form to API
async function submitAcademicForm() {
  const currentSem = parseInt(document.getElementById("currentSemester").value) || 1;
  const sgpaInputs = document.querySelectorAll(".sem-sgpa-input");
  const regInputs = document.querySelectorAll(".sem-reg-input");
  const clearedInputs = document.querySelectorAll(".sem-cleared-input");
  const backlogsInputs = document.querySelectorAll(".sem-backlogs-input");

  const semesters = [];
  sgpaInputs.forEach((inp, i) => {
    semesters.push({
      semester_number: parseInt(inp.dataset.sem),
      sgpa: parseFloat(inp.value) || 0.0,
      credits_registered: parseInt(regInputs[i]?.value) || 20,
      credits_cleared: parseInt(clearedInputs[i]?.value) || 20,
      backlogs_count: parseInt(backlogsInputs[i]?.value) || 0
    });
  });

  const subjects = [];
  const subjRows = document.querySelectorAll("#subject-rows-container tr");
  subjRows.forEach(tr => {
    const code = tr.querySelector(".subj-code")?.value.trim();
    const name = tr.querySelector(".subj-name")?.value.trim();
    const credits = parseInt(tr.querySelector(".subj-credits")?.value) || 3;
    const internal = parseFloat(tr.querySelector(".subj-internal")?.value) || 30;
    const att = parseFloat(tr.querySelector(".subj-att")?.value) || 80;
    const grade = tr.querySelector(".subj-grade")?.value || "A";

    if (code || name) {
      subjects.push({
        subject_code: code || "SUB",
        subject_name: name || "Course Subject",
        credits: credits,
        internal_marks: internal,
        max_internal_marks: 50.0,
        attendance_pct: att,
        grade_expected: grade
      });
    }
  });

  const extracurricular = [];
  document.querySelectorAll('input[name="extracurricular"]:checked').forEach(cb => {
    extracurricular.push(cb.value);
  });

  // Computed or entered CGPA
  const cgpaVal = parseFloat(document.getElementById("live-cgpa-display").textContent) || 7.0;

  const payload = {
    roll_no: document.getElementById("rollNo").value.trim(),
    full_name: document.getElementById("fullName").value.trim(),
    email: document.getElementById("email").value.trim(),
    department: document.getElementById("department").value,
    degree_program: document.getElementById("degreeProgram").value,
    current_semester: currentSem,
    academic_year: document.getElementById("academicYear").value.trim(),
    mentor_name: document.getElementById("mentorName").value.trim(),
    overall_attendance: parseFloat(document.getElementById("overallAttendance").value) || 80.0,
    cgpa: cgpaVal,
    active_backlogs: parseInt(document.getElementById("activeBacklogs").value) || 0,
    weekly_study_hours: document.getElementById("weeklyStudyHours").value,
    sleep_hours: document.getElementById("sleepHours").value,
    stress_level: document.getElementById("stressLevel").value,
    career_goal: document.getElementById("careerGoal").value,
    extracurricular_activities: extracurricular,
    semesters: semesters,
    subjects: subjects
  };

  try {
    const res = await fetch("/api/submissions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();

    if (result.success) {
      showToast("Academic Performance Successfully Analyzed!");
      currentStudentId = result.student_id;
      // Load details into dashboard and display
      await loadStudentDashboard(currentStudentId);
      switchTab("dashboard");
    } else {
      showToast("Error: " + (result.error || "Submission failed"), false);
    }
  } catch (err) {
    showToast("Server connection error", false);
    console.error(err);
  }
}

// Load Specific Student Dashboard
async function loadStudentDashboard(studentId) {
  try {
    const res = await fetch(`/api/submissions/${studentId}`);
    const data = await res.json();

    if (!data.success) {
      showToast("Unable to load student record", false);
      return;
    }

    currentStudentId = studentId;
    renderDashboard(data.student, data.semesters, data.subjects, data.analysis);
  } catch (err) {
    console.error("Dashboard error:", err);
  }
}

// Fetch latest or first student for initial dashboard display
async function fetchLatestOrFirstStudent() {
  try {
    const res = await fetch("/api/submissions");
    const data = await res.json();
    if (data.students && data.students.length > 0) {
      loadStudentDashboard(data.students[0].id);
    }
  } catch (e) {
    console.log(e);
  }
}

// Render Dashboard Data & Charts
function renderDashboard(student, semesters, subjects, analysis) {
  // Top Banner
  document.getElementById("dash-name").textContent = student.full_name;
  document.getElementById("dash-roll").textContent = student.roll_no;
  document.getElementById("dash-dept").textContent = student.department;
  document.getElementById("dash-program").textContent = student.degree_program;
  document.getElementById("dash-sem").textContent = student.current_semester;
  document.getElementById("dash-mentor").textContent = student.mentor_name || "Unassigned";

  // Initials for avatar
  const initials = student.full_name.split(" ").map(n => n[0]).slice(0, 2).join("").toUpperCase();
  document.getElementById("dash-avatar").textContent = initials || "ST";

  // Standing Badge
  document.getElementById("dash-standing-badge").textContent = analysis.standing;

  // Risk Badge & Color
  const riskBadge = document.getElementById("dash-risk-badge");
  riskBadge.innerHTML = `<i class="fa-solid fa-shield-halved"></i> <span>${analysis.risk_level} (Score: ${analysis.risk_score}/100)</span>`;
  
  if (analysis.risk_level === "Low Risk") {
    riskBadge.className = "px-3 py-1 bg-emerald-50 border border-emerald-300 text-emerald-700 text-xs font-bold rounded-full flex items-center space-x-1";
  } else if (analysis.risk_level === "Moderate Risk") {
    riskBadge.className = "px-3 py-1 bg-amber-50 border border-amber-300 text-amber-700 text-xs font-bold rounded-full flex items-center space-x-1";
  } else {
    riskBadge.className = "px-3 py-1 bg-rose-50 border border-rose-300 text-rose-700 text-xs font-bold rounded-full flex items-center space-x-1";
  }

  // 4 KPIs
  document.getElementById("dash-kpi-cgpa").textContent = Number(analysis.cgpa).toFixed(2);
  const trajEl = document.getElementById("dash-kpi-trajectory");
  const deltaStr = analysis.trajectory_delta >= 0 ? `+${analysis.trajectory_delta}` : `${analysis.trajectory_delta}`;
  trajEl.innerHTML = `<i class="fa-solid fa-${analysis.trajectory_delta >= 0 ? 'arrow-trend-up' : 'arrow-trend-down'}"></i> <span>${analysis.trajectory_status} (${deltaStr})</span>`;
  trajEl.className = analysis.trajectory_delta >= 0 ? "text-xs font-medium text-emerald-600 mt-2 flex items-center space-x-1" : "text-xs font-medium text-rose-600 mt-2 flex items-center space-x-1";

  document.getElementById("dash-kpi-attendance").textContent = Number(student.overall_attendance).toFixed(1);
  const attStatusEl = document.getElementById("dash-kpi-att-status");
  if (student.overall_attendance >= 75) {
    attStatusEl.className = "text-xs font-medium text-emerald-600 mt-2 flex items-center space-x-1";
    attStatusEl.innerHTML = `<i class="fa-solid fa-check"></i> <span>Exam Eligible (>= 75% cutoff)</span>`;
  } else {
    attStatusEl.className = "text-xs font-medium text-rose-600 mt-2 flex items-center space-x-1";
    attStatusEl.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> <span>Attendance Debarment Risk (< 75%)</span>`;
  }

  document.getElementById("dash-kpi-credits").textContent = analysis.total_credits_cleared || (student.current_semester * 22);
  document.getElementById("dash-kpi-credits-total").textContent = `/ ${analysis.total_credits_registered || (student.current_semester * 22)} registered`;
  document.getElementById("dash-kpi-credit-rate").textContent = `${analysis.credit_completion_rate}% Credit Velocity`;

  document.getElementById("dash-kpi-backlogs").textContent = student.active_backlogs;
  const backlogNote = document.getElementById("dash-kpi-backlog-note");
  if (student.active_backlogs === 0) {
    backlogNote.className = "text-xs font-medium text-emerald-600 mt-2";
    backlogNote.textContent = "All registered courses cleared";
  } else {
    backlogNote.className = "text-xs font-medium text-rose-600 mt-2";
    backlogNote.textContent = `${student.active_backlogs} pending subject remedial clearance`;
  }

  // Advisor Note
  document.getElementById("dash-advisor-note").value = student.advisor_notes || "";

  // SWOT: Strengths
  const strengthsList = document.getElementById("dash-strengths-list");
  strengthsList.innerHTML = "";
  if (analysis.strengths && analysis.strengths.length > 0) {
    analysis.strengths.forEach(s => {
      const li = document.createElement("li");
      li.className = "flex items-start space-x-2";
      li.innerHTML = `<i class="fa-solid fa-circle-check text-emerald-500 mt-0.5"></i> <span>${s}</span>`;
      strengthsList.appendChild(li);
    });
  } else {
    strengthsList.innerHTML = `<li class="text-slate-400 italic">No significant strengths flagged.</li>`;
  }

  // SWOT: Weaknesses
  const weaknessesList = document.getElementById("dash-weaknesses-list");
  weaknessesList.innerHTML = "";
  if (analysis.weaknesses && analysis.weaknesses.length > 0) {
    analysis.weaknesses.forEach(w => {
      const li = document.createElement("li");
      li.className = "flex items-start space-x-2";
      li.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-amber-500 mt-0.5"></i> <span>${w}</span>`;
      weaknessesList.appendChild(li);
    });
  } else {
    weaknessesList.innerHTML = `<li class="text-slate-400 italic">No critical academic bottlenecks detected. Consistent track record.</li>`;
  }

  // SWOT: Recommendations
  const recList = document.getElementById("dash-recommendations-list");
  recList.innerHTML = "";
  if (analysis.recommendations && analysis.recommendations.length > 0) {
    analysis.recommendations.forEach((rec, idx) => {
      const div = document.createElement("div");
      div.className = "bg-white/10 p-3 rounded-xl border border-white/10 flex items-start space-x-3";
      div.innerHTML = `
        <span class="w-6 h-6 rounded-lg bg-brand-500 text-white font-bold flex items-center justify-center text-xs shrink-0">${idx + 1}</span>
        <span class="leading-relaxed">${rec}</span>
      `;
      recList.appendChild(div);
    });
  }

  // Render Charts
  renderCharts(semesters, subjects, analysis.radar_scores);
}

// Render Charts with Chart.js
function renderCharts(semesters, subjects, radarScores) {
  // 1. GPA Trend Line Chart
  const gpaCtx = document.getElementById("gpaTrendChart").getContext("2d");
  if (gpaChartInstance) gpaChartInstance.destroy();

  const semLabels = semesters.map(s => `Sem ${s.semester_number}`);
  const sgpaData = semesters.map(s => s.sgpa);
  
  // Compute cumulative moving averages
  let runPoints = 0;
  let runCredits = 0;
  const cgpaData = semesters.map(s => {
    runPoints += (s.sgpa * s.credits_registered);
    runCredits += s.credits_registered;
    return runCredits > 0 ? (runPoints / runCredits).toFixed(2) : s.sgpa;
  });

  gpaChartInstance = new Chart(gpaCtx, {
    type: "line",
    data: {
      labels: semLabels.length ? semLabels : ["Current Sem"],
      datasets: [
        {
          label: "Semester SGPA",
          data: sgpaData.length ? sgpaData : [8.0],
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59, 130, 246, 0.1)",
          fill: true,
          tension: 0.35,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointBackgroundColor: "#2563eb",
          borderWidth: 2.5
        },
        {
          label: "Cumulative CGPA",
          data: cgpaData.length ? cgpaData : [8.0],
          borderColor: "#10b981",
          borderDash: [5, 5],
          tension: 0.2,
          pointRadius: 4,
          pointBackgroundColor: "#059669",
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          min: 4,
          max: 10,
          ticks: { stepSize: 1, color: "#64748b" },
          grid: { color: "#f1f5f9" }
        },
        x: {
          ticks: { color: "#64748b" },
          grid: { display: false }
        }
      },
      plugins: {
        legend: { position: "top", labels: { boxWidth: 12, font: { size: 11 } } },
        tooltip: { padding: 10, cornerRadius: 8 }
      }
    }
  });

  // 2. Holistic Performance Radar Chart
  const radarCtx = document.getElementById("radarChart").getContext("2d");
  if (radarChartInstance) radarChartInstance.destroy();

  const radarLabels = Object.keys(radarScores || {});
  const radarValues = Object.values(radarScores || {});

  radarChartInstance = new Chart(radarCtx, {
    type: "radar",
    data: {
      labels: radarLabels,
      datasets: [{
        label: "Score (%)",
        data: radarValues,
        backgroundColor: "rgba(99, 102, 241, 0.2)",
        borderColor: "#6366f1",
        pointBackgroundColor: "#4f46e5",
        pointBorderColor: "#fff",
        pointHoverBackgroundColor: "#fff",
        pointHoverBorderColor: "#4f46e5",
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min: 0,
          max: 100,
          ticks: { display: false, stepSize: 20 },
          pointLabels: { font: { size: 10, weight: "bold" }, color: "#475569" },
          grid: { color: "#e2e8f0" }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });

  // 3. Subject Marks vs Attendance Bar Chart
  const subjCtx = document.getElementById("subjectBarChart").getContext("2d");
  if (subjectChartInstance) subjectChartInstance.destroy();

  const subjLabels = subjects.map(s => s.subject_code);
  const marksPcts = subjects.map(s => ((s.internal_marks / (s.max_internal_marks || 50)) * 100).toFixed(1));
  const attData = subjects.map(s => s.attendance_pct);

  subjectChartInstance = new Chart(subjCtx, {
    type: "bar",
    data: {
      labels: subjLabels.length ? subjLabels : ["Course A", "Course B"],
      datasets: [
        {
          label: "Internal Assessment (%)",
          data: marksPcts.length ? marksPcts : [80, 85],
          backgroundColor: "#3b82f6",
          borderRadius: 6,
          barPercentage: 0.6
        },
        {
          label: "Subject Attendance (%)",
          data: attData.length ? attData : [90, 85],
          backgroundColor: "#10b981",
          borderRadius: 6,
          barPercentage: 0.6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          min: 0,
          max: 100,
          ticks: { stepSize: 20, color: "#64748b" },
          grid: { color: "#f1f5f9" }
        },
        x: {
          ticks: { color: "#64748b", font: { weight: "600" } },
          grid: { display: false }
        }
      },
      plugins: {
        legend: { position: "top", labels: { boxWidth: 12, font: { size: 11 } } },
        tooltip: {
          callbacks: {
            title: (items) => {
              const idx = items[0].dataIndex;
              return `${subjects[idx]?.subject_code || ''}: ${subjects[idx]?.subject_name || ''}`;
            }
          }
        }
      }
    }
  });
}

// Save Advisor Notes
async function saveAdvisorNote() {
  if (!currentStudentId) {
    showToast("No active student selected", false);
    return;
  }
  const noteText = document.getElementById("dash-advisor-note").value.trim();
  try {
    const res = await fetch(`/api/submissions/${currentStudentId}/notes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ advisor_notes: noteText })
    });
    const result = await res.json();
    if (result.success) {
      showToast("Advisor remarks recorded successfully!");
    } else {
      showToast("Failed to save note", false);
    }
  } catch (e) {
    showToast("Network error saving notes", false);
  }
}

// Load Faculty Cohort Analytics
async function loadCohortAnalytics() {
  try {
    const res = await fetch("/api/analytics");
    const data = await res.json();
    if (!data.success) return;

    const a = data.analytics;
    document.getElementById("cohort-total-students").textContent = a.total_students;
    document.getElementById("cohort-avg-cgpa").textContent = a.avg_cgpa.toFixed(2);
    document.getElementById("cohort-at-risk").textContent = a.at_risk_count;
    document.getElementById("cohort-attendance-alerts").textContent = a.attendance_alert_count;

    // Render Department Comparison Chart
    const deptCtx = document.getElementById("deptComparisonChart").getContext("2d");
    if (deptChartInstance) deptChartInstance.destroy();

    const deptLabels = a.department_stats.map(d => d.department.replace("Engineering", "Engg"));
    const deptCgpas = a.department_stats.map(d => d.avg_cgpa);
    const deptAtts = a.department_stats.map(d => d.avg_att);

    deptChartInstance = new Chart(deptCtx, {
      type: "bar",
      data: {
        labels: deptLabels,
        datasets: [
          {
            label: "Average CGPA",
            data: deptCgpas,
            backgroundColor: "#4f46e5",
            borderRadius: 6,
            yAxisID: "y"
          },
          {
            label: "Average Attendance %",
            data: deptAtts,
            backgroundColor: "#10b981",
            borderRadius: 6,
            yAxisID: "y1"
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            type: "linear",
            display: true,
            position: "left",
            min: 0,
            max: 10,
            title: { display: true, text: "CGPA (0-10)", font: { size: 10 } }
          },
          y1: {
            type: "linear",
            display: true,
            position: "right",
            min: 0,
            max: 100,
            grid: { drawOnChartArea: false },
            title: { display: true, text: "Attendance %", font: { size: 10 } }
          },
          x: {
            ticks: { font: { size: 10 } }
          }
        },
        plugins: {
          legend: { position: "top", labels: { boxWidth: 12, font: { size: 11 } } }
        }
      }
    });

    // Render Risk Distribution Donut Chart
    const donutCtx = document.getElementById("riskDonutChart").getContext("2d");
    if (riskDonutInstance) riskDonutInstance.destroy();

    const riskKeys = ["Low Risk", "Moderate Risk", "High Risk", "Critical Risk"];
    const riskCounts = riskKeys.map(k => a.risk_distribution[k] || 0);

    riskDonutInstance = new Chart(donutCtx, {
      type: "doughnut",
      data: {
        labels: riskKeys,
        datasets: [{
          data: riskCounts,
          backgroundColor: ["#10b981", "#f59e0b", "#f97316", "#ef4444"],
          borderWidth: 2,
          borderColor: "#fff"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom", labels: { boxWidth: 10, font: { size: 10 } } }
        },
        cutout: "65%"
      }
    });

  } catch (err) {
    console.error("Error loading cohort analytics:", err);
  }
}

// Load Student Directory Table
async function loadStudentDirectory() {
  const search = document.getElementById("faculty-search").value.trim();
  const dept = document.getElementById("faculty-dept-filter").value;
  const risk = document.getElementById("faculty-risk-filter").value;

  const url = `/api/submissions?search=${encodeURIComponent(search)}&department=${encodeURIComponent(dept)}&risk_level=${encodeURIComponent(risk)}`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    if (!data.success) return;

    const tbody = document.getElementById("student-directory-tbody");
    tbody.innerHTML = "";

    if (data.students.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" class="py-6 text-center text-xs text-slate-400">
            No matching student records found.
          </td>
        </tr>
      `;
      return;
    }

    data.students.forEach(st => {
      const tr = document.createElement("tr");
      tr.className = "hover:bg-slate-50 transition-colors";

      let riskBadgeClass = "bg-emerald-50 text-emerald-700 border-emerald-200";
      if (st.risk_level.includes("Moderate")) riskBadgeClass = "bg-amber-50 text-amber-700 border-amber-200";
      else if (st.risk_level.includes("High") || st.risk_level.includes("Critical")) riskBadgeClass = "bg-rose-50 text-rose-700 border-rose-200";

      tr.innerHTML = `
        <td class="py-3 px-4">
          <div class="font-bold text-slate-900">${st.full_name}</div>
          <div class="text-xs text-slate-400 font-mono">${st.roll_no} &bull; ${st.email}</div>
        </td>
        <td class="py-3 px-4 text-xs font-medium text-slate-700">${st.department}</td>
        <td class="py-3 px-4 text-xs font-semibold text-slate-600">Sem ${st.current_semester}</td>
        <td class="py-3 px-4 text-xs font-extrabold text-brand-600">${Number(st.cgpa).toFixed(2)}</td>
        <td class="py-3 px-4 text-xs font-semibold ${st.overall_attendance < 75 ? 'text-rose-600' : 'text-slate-700'}">
          ${Number(st.overall_attendance).toFixed(1)}%
          ${st.overall_attendance < 75 ? '<i class="fa-solid fa-triangle-exclamation text-rose-500 ml-1"></i>' : ''}
        </td>
        <td class="py-3 px-4 text-xs font-semibold ${st.active_backlogs > 0 ? 'text-rose-600 font-bold' : 'text-slate-500'}">
          ${st.active_backlogs}
        </td>
        <td class="py-3 px-4">
          <span class="px-2.5 py-1 text-[11px] font-bold rounded-full border ${riskBadgeClass}">
            ${st.risk_level}
          </span>
        </td>
        <td class="py-3 px-4 text-center">
          <button onclick="viewStudentAnalysis(${st.id})" 
                  class="px-3 py-1.5 bg-brand-50 hover:bg-brand-100 text-brand-700 font-semibold rounded-lg text-xs transition border border-brand-200 flex items-center space-x-1 mx-auto">
            <i class="fa-solid fa-chart-column"></i>
            <span>View Analysis</span>
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error("Directory loading error:", err);
  }
}

// Switch to student analysis view from directory table
async function viewStudentAnalysis(studentId) {
  await loadStudentDashboard(studentId);
  switchTab("dashboard");
}
