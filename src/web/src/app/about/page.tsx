import React from 'react'; // version 18.2.0
import { Metadata } from 'next'; // version ^13.4.0
import Image from 'next/image'; // version ^13.4.0
import Link from 'next/link'; // version ^13.4.0

import PageHeader from '../../components/shared/PageHeader';
import SectionHeader from '../../components/shared/SectionHeader';
import MetaTags from '../../components/shared/MetaTags';
import ImageWithFallback from '../../components/shared/ImageWithFallback';
import ResponsiveVideo from '../../components/shared/ResponsiveVideo';

import { generateMetadata as generateMetaData } from '../../utils/seo';
import { getPageBySlug, getTeamMembers } from '../../services/contentService';
import { ROUTES } from '../../constants/routes';
import { Page, TeamMember } from '../../types/content';

// Company mission statement
const MISSION_STATEMENT = 'IndiVillage is dedicated to providing cutting-edge AI-as-a-service solutions while creating sustainable livelihoods in rural communities. Our dual mission combines technological excellence with positive social impact.';

// Company core values
const COMPANY_VALUES = [
  {
    title: 'Excellence',
    description: 'We are committed to delivering the highest quality AI solutions that exceed client expectations.',
    icon: '/images/values/excellence.svg'
  },
  {
    title: 'Innovation',
    description: 'We continuously explore new technologies and approaches to solve complex challenges.',
    icon: '/images/values/innovation.svg'
  },
  {
    title: 'Impact',
    description: 'We measure our success by the positive change we create in communities and for our clients.',
    icon: '/images/values/impact.svg'
  },
  {
    title: 'Integrity',
    description: 'We operate with transparency, honesty, and ethical responsibility in all our actions.',
    icon: '/images/values/integrity.svg'
  }
];

// Company history timeline
const COMPANY_HISTORY = [
  {
    year: '2012',
    title: 'Foundation',
    description: 'IndiVillage was founded with a vision to create technology jobs in rural India.'
  },
  {
    year: '2015',
    title: 'First Center',
    description: 'Opened our first rural technology center in Ramanagara, Karnataka.'
  },
  {
    year: '2018',
    title: 'AI Focus',
    description: 'Shifted focus to AI services, leveraging our skilled workforce for data annotation and model training.'
  },
  {
    year: '2020',
    title: 'Expansion',
    description: 'Expanded operations to multiple locations and launched comprehensive AI-as-a-service offerings.'
  },
  {
    year: '2023',
    title: 'Global Impact',
    description: 'Serving clients worldwide while creating over 1,000 jobs in rural communities.'
  }
];

/**
 * Generate metadata for the About page using Next.js App Router metadata API
 */
export async function generateMetadata(): Promise<Metadata> {
  return generateMetaData({
    title: 'About Us',
    description: "Learn about IndiVillage's mission to provide AI-powered solutions with positive social impact. Discover our values, history, and the team behind our success.",
    keywords: ['About IndiVillage', 'AI company', 'social impact', 'AI for good', 'values', 'mission', 'leadership team'],
    section: 'About'
  });
}

/**
 * About page component that presents IndiVillage's mission, vision, values, and history
 */
export default async function AboutPage(): Promise<JSX.Element> {
  // Fetch About page content from CMS
  const aboutPage = await getPageBySlug('about');
  
  // Fetch featured team members
  const featuredTeamMembers = await getTeamMembers({ featured: true });

  return (
    <main className="about-page">
      <MetaTags 
        title="About Us" 
        description="Learn about IndiVillage's mission to provide AI-powered solutions with positive social impact" 
      />
      
      <PageHeader
        title="About Us"
        breadcrumbs={[
          { label: 'Home', href: ROUTES.HOME },
          { label: 'About Us', href: ROUTES.ABOUT.INDEX, current: true }
        ]}
      />
      
      {/* Mission Section */}
      <section className="mission-section">
        <div className="container mx-auto py-12 px-4 md:px-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div className="mission-content">
              <SectionHeader
                title="Our Mission"
                subtitle="AI-Powered Solutions with Social Impact"
              />
              
              <p className="text-lg mb-6">
                {aboutPage?.content || MISSION_STATEMENT}
              </p>
              
              <p className="text-lg mb-6">
                At IndiVillage, we believe that technological excellence and social responsibility 
                go hand in hand. Our innovative AI solutions not only help businesses thrive in 
                the digital age but also create sustainable employment opportunities in 
                underserved rural communities.
              </p>
              
              <div className="stats-container grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8">
                <div className="stat-item text-center">
                  <div className="text-3xl font-bold text-primary">1,000+</div>
                  <div className="text-sm">Jobs Created</div>
                </div>
                <div className="stat-item text-center">
                  <div className="text-3xl font-bold text-primary">10+</div>
                  <div className="text-sm">Communities</div>
                </div>
                <div className="stat-item text-center">
                  <div className="text-3xl font-bold text-primary">50,000+</div>
                  <div className="text-sm">Lives Transformed</div>
                </div>
                <div className="stat-item text-center">
                  <div className="text-3xl font-bold text-primary">70%</div>
                  <div className="text-sm">Women Employed</div>
                </div>
              </div>
            </div>
            
            <div className="mission-image">
              <ImageWithFallback
                src={aboutPage?.featuredImage?.url || "/images/about/mission.jpg"}
                alt="IndiVillage Mission"
                width={600}
                height={400}
                className="rounded-lg shadow-lg"
                objectFit="cover"
              />
            </div>
          </div>
        </div>
      </section>
      
      {/* Values Section */}
      <section className="values-section bg-gray-50">
        <div className="container mx-auto py-12 px-4 md:px-6">
          <SectionHeader
            title="Our Values"
            subtitle="The principles that guide our work"
            align="center"
          />
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mt-10">
            {COMPANY_VALUES.map((value, index) => (
              <div key={index} className="value-card bg-white p-6 rounded-lg shadow-md text-center">
                <div className="icon-container mx-auto mb-4 w-16 h-16 flex items-center justify-center">
                  <ImageWithFallback
                    src={value.icon}
                    alt={value.title}
                    width={48}
                    height={48}
                  />
                </div>
                <h3 className="text-xl font-semibold mb-2">{value.title}</h3>
                <p className="text-gray-600">{value.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* History Section */}
      <section className="history-section">
        <div className="container mx-auto py-12 px-4 md:px-6">
          <SectionHeader
            title="Our History"
            subtitle="The journey from vision to impact"
            align="center"
          />
          
          <div className="timeline mt-10">
            {COMPANY_HISTORY.map((milestone, index) => (
              <div key={index} className={`timeline-item flex mb-8 ${index % 2 === 0 ? 'flex-row' : 'flex-row-reverse'}`}>
                <div className="timeline-badge w-24 flex-none flex items-center justify-center">
                  <div className="year-badge bg-primary text-white px-3 py-1 rounded-full font-bold">
                    {milestone.year}
                  </div>
                </div>
                <div className="timeline-content bg-white p-6 rounded-lg shadow-md flex-1 mx-4">
                  <h3 className="text-xl font-semibold mb-2">{milestone.title}</h3>
                  <p className="text-gray-600">{milestone.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* Team Section */}
      <section className="team-section bg-gray-50">
        <div className="container mx-auto py-12 px-4 md:px-6">
          <SectionHeader
            title="Our Team"
            subtitle="The people behind our success"
            align="center"
            actionText="View Leadership Team"
            actionHref={ROUTES.ABOUT.LEADERSHIP}
          />
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8 mt-10">
            {featuredTeamMembers.map((member: TeamMember) => (
              <div key={member.id} className="team-member-card bg-white rounded-lg shadow-md overflow-hidden">
                <div className="team-member-image relative h-64">
                  <ImageWithFallback
                    src={member.photo?.url || "/images/about/placeholder-person.jpg"}
                    alt={member.name}
                    width={300}
                    height={300}
                    className="object-cover w-full h-full"
                  />
                </div>
                <div className="team-member-info p-4">
                  <h3 className="text-lg font-semibold mb-1">{member.name}</h3>
                  <p className="text-gray-600 text-sm mb-3">{member.title}</p>
                  <div className="team-member-social flex space-x-3">
                    {member.socialLinks?.linkedin && (
                      <a href={member.socialLinks.linkedin} target="_blank" rel="noopener noreferrer" 
                        className="text-gray-400 hover:text-primary transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z" />
                        </svg>
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="text-center mt-10">
            <Link href={ROUTES.ABOUT.LEADERSHIP} className="btn btn--primary">
              Meet Our Full Leadership Team
            </Link>
          </div>
        </div>
      </section>
      
      {/* Culture Section */}
      <section className="culture-section">
        <div className="container mx-auto py-12 px-4 md:px-6">
          <SectionHeader
            title="Our Culture"
            subtitle="Creating impact through technology and community"
            align="center"
          />
          
          <div className="video-container mt-10 max-w-4xl mx-auto">
            <ResponsiveVideo 
              src={aboutPage?.sections?.find(s => s.type === 'video')?.url || "https://www.youtube.com/watch?v=example"}
              title="IndiVillage Culture"
              poster="/images/about/video-poster.jpg"
              aspectRatio="16:9"
              controls
              muted
            />
          </div>
          
          <div className="culture-content mt-12 max-w-3xl mx-auto text-center">
            <p className="text-lg mb-6">
              At IndiVillage, we've built a culture of excellence, innovation, and impact. 
              We believe in empowering our team members to grow professionally while making 
              a meaningful difference in their communities.
            </p>
            
            <div className="culture-cta mt-8">
              <Link href={ROUTES.ABOUT.CAREERS} className="btn btn--primary mr-4">
                Join Our Team
              </Link>
              <Link href={ROUTES.IMPACT.INDEX} className="btn btn--secondary">
                Explore Our Impact
              </Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}