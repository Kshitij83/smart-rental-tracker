import emailjs from '@emailjs/browser'

// Simple test to debug EmailJS
export class SimpleEmailTest {
  static async testWithContactFormTemplate(): Promise<{ success: boolean; error?: string }> {
    try {
      // Initialize with your credentials
      emailjs.init('rNUrJGG1_cyzTokDj')

      // Test with contact form template variables (what your template expects)
      const templateParams = {
        from_name: 'Equipment Management System',
        from_email: 'noreply@equipment.com',
        subject: 'Equipment Alert - EQX1027',
        message: 'Equipment EQX1027 (Grader) is due for return on 9/17/2025 (12 days remaining). Priority: HIGH PRIORITY. Site: S027.'
      }

      console.log('Testing with contact form template variables:', templateParams)

      const response = await emailjs.send(
        'service_b55jyth',
        'template_6fnnn1s',
        templateParams
      )

      console.log('Email sent successfully:', response)
      return { success: true }

    } catch (error: any) {
      console.error('Email test failed:', error)
      return { 
        success: false, 
        error: `Status: ${error.status}, Message: ${error.text || error.message}` 
      }
    }
  }

  static async testWithEquipmentTemplate(): Promise<{ success: boolean; error?: string }> {
    try {
      // Initialize with your credentials
      emailjs.init('rNUrJGG1_cyzTokDj')

      // Test with equipment template variables (what our code sends)
      const templateParams = {
        equipment_id: 'EQX1027',
        equipment_type: 'Grader',
        site_id: 'S027',
        due_date: '9/17/2025',
        days_remaining: 12,
        utilization: 85,
        priority: 'HIGH PRIORITY',
        alert_type: 'Equipment Return Alert',
        message: 'Equipment EQX1027 (Grader) is due for return on 9/17/2025 (12 days remaining). Priority: HIGH PRIORITY. Site: S027.',
        timestamp: new Date().toLocaleString()
      }

      console.log('Testing with equipment template variables:', templateParams)

      const response = await emailjs.send(
        'service_b55jyth',
        'template_6fnnn1s',
        templateParams
      )

      console.log('Email sent successfully:', response)
      return { success: true }

    } catch (error: any) {
      console.error('Email test failed:', error)
      return { 
        success: false, 
        error: `Status: ${error.status}, Message: ${error.text || error.message}` 
      }
    }
  }
}
