// theme.ts
import { createTheme } from '@mui/material/styles'

const theme = createTheme({
	palette: {
		mode: 'dark',
		primary: {
			main: '#4B3FD7',
			light: '#FFFFFF',
			contrastText: '#FFFFFF'
			
		},
		// background: {
		// 	default: '#000000', // Black background
		// 	paper: '#121212', // Dark grey paper background
		// },
		// text: {
		// 	primary: '#00ff00', // Bright green text
		// },
	},
	typography: {
		fontFamily: 'Kanit, sans-serif',
		allVariants: {
			fontWeight: 'bold'
		} // Monospaced font
		
	},
	// components: {
	// 	MuiTypography: {
	// 		defaultProps: {
	// 			fontWeight: 600
	// 		}
	// 	}
	// }
})

export default theme
