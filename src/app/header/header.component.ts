import { Component, OnInit } from '@angular/core';

import { NavButton } from '../classes';
import { HeadButtonService } from '../head-button.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit {
  buttons: NavButton[];
  
  constructor(private headButtonService: HeadButtonService) { }

  ngOnInit() {
    this.getButtons();
  }
  
  getButtons(): void {
    this.headButtonService.getButtons()
      .subscribe(buttons => this.buttons = buttons);
  }
  
}
