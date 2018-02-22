// A small encircled question mark that serves as a quick-help of sorts
// Pops up with both a brief and a link to the full help page pertaining to whatever feature
import {
  Component,
  OnInit,
  Input,
  HostListener,
  ElementRef
} from '@angular/core';
import { HelpService } from '../help.service';

@Component({
    selector: 'whatsthis',
    template: `
      <div>
        <span
          class="owo"
          (click)="showLink=true"
          tooltip [content]="content" [attr.ident]="ident" [attr.relative]="!relative"
        ></span>
        <span
          class="link"
          [attr.data-ident]="ident"
          [class.visible]="showLink"
        ><a [routerLink]="linkUrl">{{linkText}}</a></span>
      </div>
    `,
    styleUrls: ['./help-tooltip.component.css']
})

export class HelpTooltipComponent implements OnInit {
    @Input() ident: string;
    @Input() relative = true;
    // `relative` is input as the opposite of what it should be;
    // this is so I can write <tag ... relative> instead of <tag ... relative="meaningless value but evals to truthy">
    showLink: boolean = false;
    linkText: string;
    linkUrl: string;
    content: string;

  constructor(
    private elementRef: ElementRef,
    private helpService: HelpService
  ) {}

  ngOnInit() {
    this.linkUrl = `/help/${this.ident}`
    this.helpService.getBrief(this.ident)
      .subscribe(resp => {this.linkText = resp.help.title; this.content = resp.help.brief});
  }
  
  @HostListener('document:click', ['$event.target'])
  determineLinkVisibility(target) {
    // Like in tooltip.directive, check if user is clicking outside of this element's bounds
    // and if so hide the element
    this.showLink = this.elementRef.nativeElement.contains(target);
  }
}
