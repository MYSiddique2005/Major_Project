// Cover-page details. The bracketed fields are for the student to fill in. Personal numbers (student ID,
// passport) go in src/meta.local.js, which is not committed and overrides the fields below.
const fields = {
  title: 'IntelliERP: Evidence-Grounded Hallucination Detection and Verification for LLM-Based ERP Decision Support',
  shortTitle: 'IntelliERP',
  student: 'Mohammad Yasin Siddique',
  studentId: '[Student ID]',
  passport: '[Passport No]',
  projectId: 'FDSIT-INTI-IU-BCSIM-AUG-2026-0003',
  home: 'G H Raisoni College of Engineering, Nagpur, India (mobility student)',
  supervisor: 'Dr. Zeyad Ahmed',
  programme: 'BCSI',
  session: 'AUGUST 2026 Session',
  submissionDate: '[DD / MM / 2026]',
};
let local = {};
try { local = require('./meta.local'); } catch (error) { /* no local details: the blanks stay */ }
module.exports = { ...fields, ...local };
