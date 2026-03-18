import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./ProfileForm.css";

const SKILL_OPTIONS = [
    "Java", "Python", "JavaScript", "React", "Spring Boot",
    "Node.js", "SQL", "MongoDB", "Docker", "AWS",
    "Machine Learning", "Cybersecurity", "Git", "REST API", "TypeScript",
];

function ProfileForm() {
    const { token } = useAuth();
    const navigate = useNavigate();

    const [form, setForm] = useState({
        firstName: "",
        lastName: "",
        email: "",
        mobile: "",
        residentialAddress: "", // NEW: Residential address field
        college: "", // College name field
        degree: "",
        studentId: "", // Changed from governmentId to studentId
        studentIdType: "college_id", // Changed from governmentIdType
    });
    const [skills, setSkills] = useState([]);
    const [resumeUrl, setResumeUrl] = useState(""); // Resume URL field
    const [message, setMessage] = useState("");
    const [messageType, setMessageType] = useState("");
    const [loading, setLoading] = useState(false);
    const [skillsOpen, setSkillsOpen] = useState(false);
    const [isEditing, setIsEditing] = useState(false); // New state for editing mode

    /* ── Load Existing Profile ─────────────────────── */
    
    useEffect(() => {
        const loadExistingProfile = async () => {
            try {
                const token = localStorage.getItem("token");
                const response = await fetch("http://localhost:5000/api/members/me", {
                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json"
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.success && data.profile) {
                        // Profile exists - populate form for editing
                        const profile = data.profile;
                        const nameParts = profile.full_name ? profile.full_name.trim().split(/\s+/) : ['', ''];
                        
                        setForm({
                            firstName: nameParts[0] || '',
                            lastName: nameParts.slice(1).join(' ') || '',
                            email: profile.email || '',
                            mobile: profile.phone_number || '',
                            residentialAddress: profile.residential_address || '', // NEW field
                            college: profile.college_name || '', // Updated to use college_name
                            degree: profile.degree || '',
                            studentId: profile.student_id || '',
                            studentIdType: profile.student_id_type || 'college_id'
                        });
                        
                        setResumeUrl(profile.resume_url || '');
                        setIsEditing(true);
                    }
                    // If no profile, stay in create mode
                } else if (response.status !== 404) {
                    // Handle other errors
                    console.error('Error checking profile:', response.status);
                }
            } catch (error) {
                console.error('Error loading profile:', error);
            }
        };

        loadExistingProfile();
    }, []);

    /* ── Handlers ──────────────────────────────── */

    const handleChange = (e) => {
        const { name, value } = e.target;
        
        // Handle student ID formatting based on type
        if (name === 'studentId') {
            const idType = form.studentIdType;
            let formatted = value;
            
            switch (idType) {
                case 'college_id':
                    // Format as CLG123456 or similar
                    const cleanCollegeId = value.toUpperCase().replace(/[^A-Z0-9]/g, '');
                    formatted = cleanCollegeId;
                    break;
                case 'enrollment_number':
                    // Format as ENR1234567890
                    const cleanEnrollment = value.toUpperCase().replace(/[^A-Z0-9]/g, '');
                    formatted = cleanEnrollment;
                    break;
                case 'roll_number':
                    // Format as ROLL123456
                    const cleanRoll = value.toUpperCase().replace(/[^A-Z0-9]/g, '');
                    formatted = cleanRoll;
                    break;
                case 'prn_number':
                    // Format as PRN12345678
                    const cleanPRN = value.toUpperCase().replace(/[^A-Z0-9]/g, '');
                    formatted = cleanPRN;
                    break;
                case 'application_id':
                    // Format as APP2024001
                    const cleanApp = value.toUpperCase().replace(/[^A-Z0-9]/g, '');
                    formatted = cleanApp;
                    break;
                default:
                    // No special formatting for other types
                    formatted = value;
            }
            
            setForm({ ...form, [name]: formatted });
        } else if (name === 'studentIdType') {
            // Clear ID when type changes
            setForm({ ...form, [name]: value, studentId: '' });
        } else {
            setForm({ ...form, [name]: value });
        }
    };

    const toggleSkill = (skill) => {
        setSkills((prev) =>
            prev.includes(skill) ? prev.filter((s) => s !== skill) : [...prev, skill]
        );
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage("");
        setMessageType("");
        setLoading(true);

        try {
            const payload = {
                full_name: `${form.firstName} ${form.lastName}`,
                email: form.email,
                phone_number: form.mobile,
                residential_address: form.residentialAddress, // NEW field
                college_name: form.college, // Updated field name
                degree: form.degree,
                resume_url: resumeUrl, // Use the resume URL field
                student_id: form.studentId, // Use actual student ID from form
            };

            // Use PUT method for updating, POST for creating
            const method = isEditing ? "PUT" : "POST";
            const url = "http://localhost:5000/api/members/me";

            const response = await fetch(url, {
                method: method,
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                const data = await response.json();
                setMessage(
                    isEditing 
                        ? "Profile updated successfully!" 
                        : "Profile created successfully!"
                );
                setMessageType("success");

                // Redirect to dashboard after successful submission
                setTimeout(() => {
                    navigate("/dashboard");
                }, 1500);
            } else {
                const errorData = await response.json();
                setMessage(
                    errorData.message || 
                    (isEditing ? "Failed to update profile." : "Failed to create profile.")
                );
                setMessageType("error");
            }
        } catch (error) {
            setMessage(
                isEditing 
                    ? "Unable to update profile. Please try again later."
                    : "Unable to create profile. Please try again later."
            );
            setMessageType("error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="profile-page">
            <div className="profile-card">
                {/* Header */}
                <div className="profile-header">
                    <div className="profile-header-icon">📋</div>
                    <h1>{isEditing ? "Edit Profile" : "Profile Application"}</h1>
                    <p>{isEditing ? "Update your internship profile details below" : "Complete your internship profile details below"}</p>
                </div>

                <form className="profile-form" onSubmit={handleSubmit}>
                    {/* ── Name Row ──────────────────────── */}
                    <div className="profile-row">
                        <div className="form-group">
                            <label htmlFor="firstName">First Name</label>
                            <input
                                id="firstName"
                                name="firstName"
                                type="text"
                                placeholder="John"
                                value={form.firstName}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="lastName">Last Name</label>
                            <input
                                id="lastName"
                                name="lastName"
                                type="text"
                                placeholder="Doe"
                                value={form.lastName}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    {/* ── Contact Row ───────────────────── */}
                    <div className="profile-row">
                        <div className="form-group">
                            <label htmlFor="email">Email</label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                placeholder="john@example.com"
                                value={form.email}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="mobile">Mobile Number</label>
                            <input
                                id="mobile"
                                name="mobile"
                                type="tel"
                                placeholder="+91 9876543210"
                                value={form.mobile}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    {/* ── Address Row ───────────────────── */}
                    <div className="profile-row">
                        <div className="form-group">
                            <label htmlFor="residentialAddress">Residential Address</label>
                            <input
                                id="residentialAddress"
                                name="residentialAddress"
                                type="text"
                                placeholder="123 Main St, Apt 4B, Mumbai, Maharashtra 400001"
                                value={form.residentialAddress}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="college">College Name</label>
                            <input
                                id="college"
                                name="college"
                                type="text"
                                placeholder="University of Mumbai"
                                value={form.college}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    {/* ── Education Row ─────────────────── */}
                    <div className="profile-row">
                        <div className="form-group">
                            <label htmlFor="degree">Degree</label>
                            <input
                                id="degree"
                                name="degree"
                                type="text"
                                placeholder="B.Tech Computer Science"
                                value={form.degree}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <div></div> {/* Empty div for layout balance */}
                        </div>
                    </div>

                    {/* ── Skills Multi-Select ───────────── */}
                    <div className="form-group">
                        <label>Skills</label>
                        <div
                            className={`skills-dropdown ${skillsOpen ? "open" : ""}`}
                            onClick={() => setSkillsOpen(!skillsOpen)}
                            onKeyDown={(e) => e.key === "Enter" && setSkillsOpen(!skillsOpen)}
                            role="listbox"
                            tabIndex={0}
                            aria-expanded={skillsOpen}
                        >
                            <div className="skills-selected">
                                {skills.length === 0
                                    ? "Select your skills…"
                                    : skills.join(", ")}
                            </div>
                            <span className="skills-arrow">{skillsOpen ? "▲" : "▼"}</span>
                        </div>
                        {skillsOpen && (
                            <div className="skills-options">
                                {SKILL_OPTIONS.map((skill) => (
                                    <label key={skill} className="skills-option">
                                        <input
                                            type="checkbox"
                                            checked={skills.includes(skill)}
                                            onChange={() => toggleSkill(skill)}
                                        />
                                        <span>{skill}</span>
                                    </label>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* ── Student ID ───────────────────── */}
                    <div className="form-group">
                        <label htmlFor="studentIdType">Student ID Type (Optional)</label>
                        <select
                            id="studentIdType"
                            name="studentIdType"
                            value={form.studentIdType}
                            onChange={handleChange}
                            className="profile-input"
                            style={{ marginBottom: '10px' }}
                        >
                            <option value="college_id">College ID</option>
                            <option value="enrollment_number">Enrollment Number</option>
                            <option value="roll_number">Roll Number</option>
                            <option value="prn_number">PRN Number</option>
                            <option value="application_id">Application ID</option>
                            <option value="other">Other</option>
                        </select>
                        
                        <label htmlFor="studentId" style={{ fontSize: '14px', fontWeight: 'normal' }}>
                            {form.studentIdType === 'college_id' && 'College ID Number'}
                            {form.studentIdType === 'enrollment_number' && 'Enrollment Number'}
                            {form.studentIdType === 'roll_number' && 'Roll Number'}
                            {form.studentIdType === 'prn_number' && 'PRN Number'}
                            {form.studentIdType === 'application_id' && 'Application ID'}
                            {form.studentIdType === 'other' && 'Student ID Number'}
                        </label>
                        <input
                            id="studentId"
                            type="text"
                            placeholder={
                                form.studentIdType === 'college_id' ? 'Enter College ID (e.g., CLG123456)' :
                                form.studentIdType === 'enrollment_number' ? 'Enter Enrollment Number (e.g., ENR1234567890)' :
                                form.studentIdType === 'roll_number' ? 'Enter Roll Number (e.g., ROLL123456)' :
                                form.studentIdType === 'prn_number' ? 'Enter PRN Number (e.g., PRN12345678)' :
                                form.studentIdType === 'application_id' ? 'Enter Application ID (e.g., APP2024001)' :
                                'Enter Student ID Number'
                            }
                            value={form.studentId}
                            onChange={handleChange}
                            name="studentId"
                            className="profile-input"
                            maxLength={50}
                        />
                        <small style={{ color: '#666', fontSize: '12px', marginTop: '5px', display: 'block' }}>
                            {form.studentIdType === 'college_id' && <><strong>College ID:</strong> Your institution-issued student ID<br/></>}
                            {form.studentIdType === 'enrollment_number' && <><strong>Enrollment:</strong> University enrollment number<br/></>}
                            {form.studentIdType === 'roll_number' && <><strong>Roll Number:</strong> Academic roll number<br/></>}
                            {form.studentIdType === 'prn_number' && <><strong>PRN:</strong> Permanent Registration Number<br/></>}
                            {form.studentIdType === 'application_id' && <><strong>Application ID:</strong> Application tracking ID<br/></>}
                            {form.studentIdType === 'other' && <><strong>Other:</strong> Any student identification number<br/></>}
                            This field is completely optional.
                        </small>
                    </div>

                    {/* ── Resume Section ────────────────── */}
                    <div className="form-group">
                        <label>Resume</label>
                        
                        {/* Resume URL Input */}
                        <div>
                            <input
                                type="url"
                                placeholder="Paste your resume URL here (Google Docs, LinkedIn, Drive, etc.)"
                                value={resumeUrl}
                                onChange={(e) => setResumeUrl(e.target.value)}
                                style={{
                                    width: '100%',
                                    padding: '10px',
                                    border: '1px solid #ddd',
                                    borderRadius: '5px',
                                    fontSize: '14px'
                                }}
                            />
                            {resumeUrl && (
                                <div style={{ marginTop: '10px' }}>
                                    <small style={{ color: '#666', display: 'block', marginBottom: '5px' }}>
                                        ✓ Resume URL added
                                    </small>
                                    <small style={{ color: '#888', fontSize: '11px', display: 'block' }}>
                                        💡 Supported: Google Docs, LinkedIn Profile, Google Drive, Dropbox, Personal Website
                                    </small>
                                    <div style={{ marginTop: '8px' }}>
                                        <a 
                                            href={resumeUrl} 
                                            target="_blank" 
                                            rel="noopener noreferrer"
                                            style={{
                                                color: '#007bff',
                                                textDecoration: 'none',
                                                fontSize: '12px',
                                                border: '1px solid #007bff',
                                                padding: '4px 8px',
                                                borderRadius: '3px',
                                                display: 'inline-block'
                                            }}
                                        >
                                            🔗 Preview Resume Link
                                        </a>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* ── Message ──────────────────────── */}
                    {message && (
                        <div className={`login-message ${messageType}`}>{message}</div>
                    )}

                    {/* ── Submit ───────────────────────── */}
                    <button
                        type="submit"
                        className="profile-submit-btn"
                        disabled={loading}
                    >
                        {loading ? "Saving…" : (isEditing ? "Update Profile" : "Save Profile")}
                    </button>
                </form>
            </div>
        </div>
    );
}

export default ProfileForm;
