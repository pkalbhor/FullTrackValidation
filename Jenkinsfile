pipeline {
  environment {
    //This variable need be tested as string
    doTest = '0'
    VOMS_CREDENTIALS = credentials('gridpass')
    JIRA_CREDENTIALS = credentials('jirapass')
  }
  agent any
  options {
    // This is required if you want to clean before build
    skipDefaultCheckout(true)
  }
  stages {
    stage('Input Processing') {
      steps{
        cleanWs()
        checkout scm
        sh('./process_input.py ${JIRA_CREDENTIALS_USR} ${JIRA_CREDENTIALS_PSW}')
        stash includes: '*.json', name: 'json'
        script {
            def props = readProperties file: 'envs.properties' 
            env.Validate = props.Validate
            env.Title = props.Title
        }
      }
    }

    stage('Test') {
      when {
        expression { doTest == '1' }
      }
      parallel {
        stage('HLT Test') {
          when {
            expression { doTest == '1' }
          }
          agent {
            label "lxplus"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
            sh('echo ${VOMS_CREDENTIALS_PSW} | voms-proxy-init --rfc --voms cms --pwstdin')
            sh('./relval_submit.py -f metadata_HLT.json --dry')
            sh('./commands_in_one_go.sh')
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
            }
          }
        }

        stage('Express Test') {
          when {
            expression { doTest == '1' }
          }
          agent {
            label "lxplus"
          }
          steps {
            cleanWs()
            checkout scm
            unstash 'json'
            sh('echo ${VOMS_CREDENTIALS_PSW} | voms-proxy-init --rfc --voms cms --pwstdin')
            sh('./relval_submit.py -f metadata_Express.json --dry')
            sh('./commands_in_one_go.sh')
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
            }
          }
        }

        stage('PR Test') {
          when {
            expression { doTest == '1' }
          }
          agent {
            label "lxplus"
          }
          steps {
            cleanWs()
            checkout scm  
            unstash 'json'
            sh('echo ${VOMS_CREDENTIALS_PSW} | voms-proxy-init --rfc --voms cms --pwstdin')
            sh('./relval_submit.py -f metadata_Prompt.json --dry')
            sh('./commands_in_one_go.sh')
          }
          post {
            success {
              archiveArtifacts(artifacts: 'cmsDrivers_*.sh', fingerprint: true)
            }
          }
        }

      }
    }
    stage('Create Jira Ticket') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        sh('./createTicket.py ${JIRA_CREDENTIALS_USR} ${JIRA_CREDENTIALS_PSW}')
      }
    }
    stage('Email') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        echo "Sending email request to AlCa Hypernews"
        emailext(body: "This is a TEST! Please ignore", subject: "[HLT/EXPRESS/PROMPT] Full track validation for ${env.Validate}", to: 'hn-cms-hnTest@cern.ch')
      }
    }
    stage('Submission') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        echo "Submitting request to Request Manager/WMAgent production tool."
      }
    }
    stage('Twiki update') {
      when {
        expression { env.Validate == 'Yes' }
      }
      steps {
        echo "Creating validation report on dedicated Twiki"
      }
    }
  }
  post {
    always {
      emailext(body: "${currentBuild.currentResult}: Job ${env.JOB_NAME} build ${env.BUILD_NUMBER}\n More info at: ${env.BUILD_URL}\n Access cosole output at: ${env.BUILD_URL}console. \n ${env.RUN_DISPLAY_URL}", recipientProviders: [[$class: 'DevelopersRecipientProvider'], [$class: 'RequesterRecipientProvider']], subject: "Jenkins Build ${currentBuild.currentResult}: Job ${env.JOB_NAME}", to: 'physics.pritam@gmail.com', attachLog: true)
    }

  }
}
