import React from 'react';
import { Metadata } from 'next';
import Image from 'next/image';
import Link from 'next/link';

import PageHeader from '../../components/shared/PageHeader';
import SectionHeader from '../../components/shared/SectionHeader';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import ImageWithFallback from '../../components/shared/ImageWithFallback';
import { generateMetadata as generateSeoMetadata } from '../../utils/seo';
import { getPageBySlug } from '../../services/contentService';
import { ROUTES } from '../../constants/routes';

export const generateMetadata = (): Metadata => {
  return generateSeoMetadata({
    title: 'Careers at IndiVillage',
    description: 'Join our team and be part of a mission to provide AI-powered solutions while creating positive social impact in rural communities',
    keywords: ['careers', 'jobs', 'employment', 'AI jobs', 'social impact careers', 'tech jobs', 'IndiVillage careers']
  });
};

const JOB_OPENINGS = [
  {
    title: 'AI Data Scientist',
    department: 'AI Development',
    location: 'Bangalore / Remote',
    type: 'Full-time',
    description: 'Design and implement machine learning models for our AI-as-a-service offerings.',
    requirements: [
      'MS/PhD in Computer Science, AI, or related field',
      '3+ years experience in machine learning and data science',
      'Proficiency in Python, TensorFlow, and PyTorch',
      'Experience with NLP and computer vision applications'
    ]
  },
  {
    title: 'Data Annotation Specialist',
    department: 'Data Operations',
    location: 'Ramanagara',
    type: 'Full-time',
    description: 'Perform high-quality data annotation and labeling for AI training datasets.',
    requirements: [
      'Bachelor\'s degree in any discipline',
      'Strong attention to detail',
      'Good English communication skills',
      'Ability to follow detailed guidelines'
    ]
  },
  {
    title: 'Project Manager',
    department: 'Operations',
    location: 'Bangalore / Hybrid',
    type: 'Full-time',
    description: 'Manage AI service delivery projects and client relationships.',
    requirements: [
      'Bachelor\'s degree in Computer Science or related field',
      '5+ years of project management experience',
      'PMP certification preferred',
      'Experience in AI/ML projects is a plus'
    ]
  },
  {
    title: 'Human-in-the-Loop Specialist',
    department: 'AI Operations',
    location: 'Ramanagara / Yeshwantpur',
    type: 'Full-time',
    description: 'Provide human oversight and quality control for AI model outputs.',
    requirements: [
      'Bachelor\'s degree in any discipline',
      'Strong analytical skills',
      'Attention to detail',
      'Basic understanding of AI concepts'
    ]
  }
];

const EMPLOYEE_BENEFITS = [
  {
    title: 'Competitive Compensation',
    description: 'Market-competitive salary packages with performance bonuses',
    icon: 'money'
  },
  {
    title: 'Health Insurance',
    description: 'Comprehensive health coverage for employees and dependents',
    icon: 'health'
  },
  {
    title: 'Professional Development',
    description: 'Learning stipends and dedicated time for skill development',
    icon: 'education'
  },
  {
    title: 'Work-Life Balance',
    description: 'Flexible work arrangements and generous paid time off',
    icon: 'balance'
  },
  {
    title: 'Social Impact',
    description: 'Be part of creating positive change in rural communities',
    icon: 'impact'
  },
  {
    title: 'Career Growth',
    description: 'Clear career paths and internal promotion opportunities',
    icon: 'career'
  }
];

const APPLICATION_STEPS = [
  {
    step: 1,
    title: 'Application Review',
    description: 'Our team reviews your application and resume'
  },
  {
    step: 2,
    title: 'Initial Screening',
    description: 'Brief phone or video call to discuss your background'
  },
  {
    step: 3,
    title: 'Technical Assessment',
    description: 'Role-specific skills evaluation'
  },
  {
    step: 4,
    title: 'Team Interviews',
    description: 'Meet with potential teammates and managers'
  },
  {
    step: 5,
    title: 'Offer',
    description: 'Receive and review your offer package'
  }
];

const EMPLOYEE_TESTIMONIALS = [
  {
    quote: 'Working at IndiVillage has given me the opportunity to grow professionally while knowing my work creates positive impact in rural communities.',
    name: 'Priya S.',
    role: 'Data Scientist',
    location: 'Bangalore',
    image: '/images/team/testimonial-1.jpg'
  },
  {
    quote: 'I started as a data annotator and have grown to lead a team of 15 people. IndiVillage truly invests in their employees\' growth.',
    name: 'Rajesh K.',
    role: 'Team Lead',
    location: 'Ramanagara',
    image: '/images/team/testimonial-2.jpg'
  },
  {
    quote: 'The culture at IndiVillage balances professional excellence with a genuine commitment to social impact. It\'s the best of both worlds.',
    name: 'Ananya M.',
    role: 'Project Manager',
    location: 'Bangalore',
    image: '/images/team/testimonial-3.jpg'
  }
];

const CareersPage = async (): Promise<JSX.Element> => {
  // Fetch careers page content
  const pageContent = await getPageBySlug('careers');
  
  // Define breadcrumbs for navigation
  const breadcrumbs = [
    { label: 'Home', href: '/' },
    { label: 'About', href: ROUTES.ABOUT.INDEX },
    { label: 'Careers', href: ROUTES.ABOUT.CAREERS, current: true }
  ];

  return (
    <div className="careers-page">
      <PageHeader
        title="Careers at IndiVillage"
        breadcrumbs={breadcrumbs}
      />
      
      {/* Introduction section */}
      <section className="section section-intro">
        <div className="section-container">
          <div className="section-content text-center">
            <h2 className="section-title">Build Your Career With Purpose</h2>
            <p className="section-description">
              At IndiVillage, we're more than just an AI services company. We're a team of passionate professionals committed to delivering exceptional technology solutions while creating sustainable employment in rural communities.
            </p>
            <p className="section-description">
              When you join our team, you become part of a mission that combines technological excellence with meaningful social impact. We believe that the best technology solutions come from diverse, motivated teams that are empowered to innovate and grow.
            </p>
            <p className="section-description">
              Our unique "AI for Good" model means your work directly contributes to creating quality jobs in underserved communities, empowering rural talent, and driving economic development where it's needed most.
            </p>
          </div>
        </div>
      </section>
      
      {/* Job openings section */}
      <section className="section section-job-openings section-alt">
        <div className="section-container">
          <SectionHeader
            title="Current Openings"
            subtitle="Explore opportunities to join our team"
            align="center"
          />
          
          <div className="job-grid">
            {JOB_OPENINGS.map((job, index) => (
              <Card key={index} className="job-card">
                <div className="job-card-content">
                  <h3 className="job-title">{job.title}</h3>
                  <div className="job-meta">
                    <span className="job-department">{job.department}</span>
                    <span className="job-location">{job.location}</span>
                  </div>
                  <p className="job-description">{job.description}</p>
                  <div className="job-requirements">
                    <h4 className="requirements-title">Requirements:</h4>
                    <ul className="requirements-list">
                      {job.requirements.map((req, i) => (
                        <li key={i} className="requirement-item">{req}</li>
                      ))}
                    </ul>
                  </div>
                  <Button variant="primary">
                    Apply Now
                  </Button>
                </div>
              </Card>
            ))}
          </div>
          
          <div className="general-application">
            <p className="general-application-text">
              Don't see a role that fits your skills? We're always looking for talented individuals to join our team.
            </p>
            <Button variant="secondary">
              Submit a General Application
            </Button>
          </div>
        </div>
      </section>
      
      {/* Benefits section */}
      <section className="section section-benefits">
        <div className="section-container">
          <SectionHeader
            title="Employee Benefits"
            subtitle="We take care of our team so they can focus on making an impact"
            align="center"
          />
          
          <div className="benefits-grid">
            {EMPLOYEE_BENEFITS.map((benefit, index) => (
              <Card key={index} className="benefit-card">
                <div className="benefit-card-content">
                  <div className="benefit-icon">
                    <Image 
                      src={`/images/icons/${benefit.icon}.svg`}
                      alt={benefit.title}
                      width={48}
                      height={48}
                    />
                  </div>
                  <h3 className="benefit-title">{benefit.title}</h3>
                  <p className="benefit-description">{benefit.description}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>
      
      {/* Culture section */}
      <section className="section section-culture section-alt section-dark">
        <div className="section-container">
          <SectionHeader
            title="Our Culture"
            subtitle="Work with purpose in a collaborative environment"
            align="center"
          />
          
          <div className="culture-grid">
            <div className="culture-content">
              <h3 className="culture-title">Innovation with Impact</h3>
              <p className="culture-description">
                We foster a culture of innovation where creative solutions are encouraged and ideas can come from anyone. Our teams work collaboratively to solve challenging problems while creating meaningful social impact.
              </p>
              <h3 className="culture-title">Growth and Development</h3>
              <p className="culture-description">
                We invest in our employees' growth through continuous learning opportunities, mentorship, and a clear path for career advancement. Your success is our success, and we're committed to helping you achieve your professional goals.
              </p>
              <h3 className="culture-title">Diversity and Inclusion</h3>
              <p className="culture-description">
                We value diverse perspectives and experiences. With team members from various backgrounds and locations across India, we've built an inclusive environment where everyone's voice matters.
              </p>
            </div>
            
            <div className="culture-images">
              <ImageWithFallback
                src="/images/careers/culture-1.jpg"
                alt="Team collaboration at IndiVillage"
                width={300}
                height={300}
                className="culture-image"
              />
              <ImageWithFallback
                src="/images/careers/culture-2.jpg"
                alt="Training session at IndiVillage"
                width={300}
                height={300}
                className="culture-image"
              />
              <ImageWithFallback
                src="/images/careers/culture-3.jpg"
                alt="Team building activity"
                width={300}
                height={300}
                className="culture-image"
              />
              <ImageWithFallback
                src="/images/careers/culture-4.jpg"
                alt="IndiVillage office space"
                width={300}
                height={300}
                className="culture-image"
              />
            </div>
          </div>
        </div>
      </section>
      
      {/* Testimonials section */}
      <section className="section section-testimonials">
        <div className="section-container">
          <SectionHeader
            title="Employee Testimonials"
            subtitle="Hear from our team members about their experience"
            align="center"
          />
          
          <div className="testimonials-grid">
            {EMPLOYEE_TESTIMONIALS.map((testimonial, index) => (
              <Card key={index} className="testimonial-card">
                <div className="testimonial-content">
                  <div className="testimonial-header">
                    <div className="testimonial-image">
                      <ImageWithFallback
                        src={testimonial.image}
                        alt={testimonial.name}
                        width={64}
                        height={64}
                        className="testimonial-avatar"
                      />
                    </div>
                    <div className="testimonial-author">
                      <h4 className="testimonial-name">{testimonial.name}</h4>
                      <p className="testimonial-role">{testimonial.role}, {testimonial.location}</p>
                    </div>
                  </div>
                  <blockquote className="testimonial-quote">"{testimonial.quote}"</blockquote>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>
      
      {/* Application process section */}
      <section className="section section-application-process section-alt">
        <div className="section-container">
          <SectionHeader
            title="Application Process"
            subtitle="What to expect when you apply"
            align="center"
          />
          
          <div className="application-steps">
            {APPLICATION_STEPS.map((step) => (
              <div key={step.step} className="application-step">
                <div className="step-number">{step.step}</div>
                <div className="step-content">
                  <h3 className="step-title">{step.title}</h3>
                  <p className="step-description">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* CTA section */}
      <section className="section section-cta section-dark">
        <div className="section-container">
          <div className="cta-content">
            <h2 className="cta-title">Ready to Join Our Team?</h2>
            <p className="cta-description">
              Take the first step towards a career that combines professional growth with meaningful social impact.
            </p>
            <div className="cta-buttons">
              <Button variant="secondary" size="large">
                View All Openings
              </Button>
              <Link href={ROUTES.CONTACT}>
                <Button variant="secondary" size="large">
                  Contact Recruitment Team
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default CareersPage;