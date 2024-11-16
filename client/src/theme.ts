// theme.ts
import { createTheme } from '@mui/material/styles'

const theme = createTheme({
	palette: {
		mode: 'dark',
		primary: {
			main: '#00ff00', // Bright green
		},
		background: {
			default: '#000000', // Black background
			paper: '#121212', // Dark grey paper background
		},
		text: {
			primary: '#00ff00', // Bright green text
		},
	},
	typography: {
		fontFamily: 'Courier New, monospace', // Monospaced font
	},
})

export default theme
